import io
import os
import zipfile
import pickle
import numpy as np
import onnx
from onnx import numpy_helper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PT_PATH = os.path.join(BASE_DIR, "weights", "best.pt")
BASE_ONNX_PATH = os.path.join(BASE_DIR, "weights", "base_yolov8n.onnx")
OUT_ONNX_PATH = os.path.join(BASE_DIR, "weights", "floorcad-yolov8n-detect.onnx")


def extract_pt_state(pt_path):
    z = zipfile.ZipFile(pt_path)
    data_bytes = z.read("best/data.pkl")

    def read_storage(key, dtype):
        return np.frombuffer(z.read(f"best/data/{key}"), dtype=dtype)

    def rebuild_tensor_v2(storage_info, storage_offset, size, stride, requires_grad, backward_hooks=None):
        tag, s_type, key, device, numel = storage_info
        s_name = s_type.__name__ if hasattr(s_type, "__name__") else str(s_type)
        dtype = np.float16 if "Half" in s_name else (np.int64 if "Long" in s_name else np.float32)
        storage = read_storage(key, dtype=dtype)
        if len(size) == 0:
            return storage[0] if len(storage) > 0 else np.array(0, dtype=dtype)
        itemsize = storage.itemsize
        byte_strides = tuple(s * itemsize for s in stride)
        arr = np.lib.stride_tricks.as_strided(storage[storage_offset:], shape=size, strides=byte_strides)
        return np.copy(arr)

    class WeightLoader(pickle.Unpickler):
        def find_class(self, module, name):
            if name == "_rebuild_tensor_v2":
                return rebuild_tensor_v2
            if name == "_rebuild_parameter":
                return lambda data, *a: data
            class Dummy:
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.name = name
                def __setstate__(self, state):
                    self.state = state
                def __repr__(self):
                    return f"<{self.name}>"
            Dummy.__name__ = name
            return Dummy

        def persistent_load(self, pid):
            return pid

    loader = WeightLoader(io.BytesIO(data_bytes))
    obj = loader.load()
    return obj


def flatten_modules(mod, prefix=""):
    modules = {}
    if hasattr(mod, "state"):
        modules[prefix.rstrip(".")] = mod
        for k, submod in mod.state.get("_modules", {}).items():
            modules.update(flatten_modules(submod, prefix=f"{prefix}{k}."))
    return modules


def convert():
    print("Loading PyTorch checkpoint from:", PT_PATH)
    pt_obj = extract_pt_state(PT_PATH)
    pt_model = pt_obj["model"]
    # If pt_model has submodule 'model', use that as base so prefixes match 'model.'
    if hasattr(pt_model, "state") and "_modules" in pt_model.state and "model" in pt_model.state["_modules"]:
        base_mod = pt_model.state["_modules"]["model"]
        all_modules = flatten_modules(base_mod, prefix="model.")
    else:
        all_modules = flatten_modules(pt_model, prefix="model.")

    print(f"Flattened {len(all_modules)} PyTorch modules. Sample keys: {list(all_modules.keys())[:5]}")

    print("Loading base ONNX graph from:", BASE_ONNX_PATH)
    onnx_model = onnx.load(BASE_ONNX_PATH)

    # Build dictionary of existing initializers
    init_map = {init.name: init for init in onnx_model.graph.initializer}
    print(f"Base ONNX has {len(init_map)} initializers.")

    # Match and fuse/update each ONNX initializer
    updated_count = 0
    new_initializers = []

    for name, init in init_map.items():
        # Case 1: Detect head convs without BatchNorm
        # e.g., model.22.cv2.0.2.weight, model.22.cv3.0.2.weight
        if any(name.startswith(f"model.22.{cv}.{i}.2.") for cv in ["cv2", "cv3"] for i in range(3)):
            # Name pattern: model.22.cv3.0.2.weight
            parts = name.split(".")
            mod_key = ".".join(parts[:-1])
            param_name = parts[-1]
            if mod_key in all_modules:
                mod = all_modules[mod_key]
                val = mod.state["_parameters"].get(param_name)
                if val is not None:
                    arr = val.astype(np.float32)
                    new_init = numpy_helper.from_array(arr, name=name)
                    new_initializers.append(new_init)
                    updated_count += 1
                    continue

        # Case 2: DFL conv weight (model.22.dfl.conv.weight)
        if name == "model.22.dfl.conv.weight":
            mod = all_modules.get("model.22.dfl.conv")
            if mod and "weight" in mod.state["_parameters"]:
                arr = mod.state["_parameters"]["weight"].astype(np.float32)
                new_init = numpy_helper.from_array(arr, name=name)
                new_initializers.append(new_init)
                updated_count += 1
                continue

        # Case 3: Standard Conv + BatchNorm fused
        # In ONNX: name is e.g. "model.0.conv.weight" and "model.0.conv.bias"
        # In PyTorch: parent module has 'conv' and 'bn' submodules
        # e.g., mod_key = "model.0" has conv and bn
        if ".conv.weight" in name or ".conv.bias" in name:
            parent_key = name.rsplit(".conv.", 1)[0]
            param_type = name.rsplit(".", 1)[-1]  # 'weight' or 'bias'

            if parent_key in all_modules:
                parent_mod = all_modules[parent_key]
                submodules = parent_mod.state.get("_modules", {})
                conv_mod = submodules.get("conv")
                bn_mod = submodules.get("bn")

                if conv_mod and bn_mod:
                    # Fuse Conv and BatchNorm
                    w_conv = conv_mod.state["_parameters"]["weight"].astype(np.float32)
                    b_conv = conv_mod.state["_parameters"].get("bias")
                    if b_conv is None:
                        b_conv = np.zeros(w_conv.shape[0], dtype=np.float32)
                    else:
                        b_conv = b_conv.astype(np.float32)

                    gamma = bn_mod.state["_parameters"]["weight"].astype(np.float32)
                    beta = bn_mod.state["_parameters"]["bias"].astype(np.float32)
                    mean = bn_mod.state["_buffers"]["running_mean"].astype(np.float32)
                    var = bn_mod.state["_buffers"]["running_var"].astype(np.float32)
                    eps = 1e-3  # Ultralytics default BatchNorm eps

                    scale = gamma / np.sqrt(var + eps)
                    w_fused = w_conv * scale.reshape(-1, 1, 1, 1)
                    b_fused = (b_conv - mean) * scale + beta

                    if param_type == "weight":
                        new_init = numpy_helper.from_array(w_fused, name=name)
                    else:
                        new_init = numpy_helper.from_array(b_fused, name=name)
                    new_initializers.append(new_init)
                    updated_count += 1
                    continue

        # Default fallback: keep existing
        new_initializers.append(init)

    print(f"Successfully fused and updated {updated_count} initializers!")

    # Replace initializers in graph
    del onnx_model.graph.initializer[:]
    onnx_model.graph.initializer.extend(new_initializers)

    # Update Constant nodes in Detect head for nc=35 (64 bbox channels + 35 class channels = 99)
    for node in onnx_model.graph.node:
        if node.op_type == "Constant":
            for attr in node.attribute:
                if attr.t:
                    arr = numpy_helper.to_array(attr.t)
                    if arr.ndim == 1 and len(arr) == 3 and arr[1] == 144:
                        # [1, 144, -1] -> [1, 99, -1]
                        new_arr = arr.copy()
                        new_arr[1] = 64 + 35  # 99
                        attr.t.CopyFrom(numpy_helper.from_array(new_arr))
                        print(f"Updated node {node.name} from [1, 144, -1] to [1, 99, -1]")
                    elif arr.ndim == 1 and len(arr) == 2 and arr[0] == 64 and arr[1] == 80:
                        # [64, 80] -> [64, 35]
                        new_arr = np.array([64, 35], dtype=arr.dtype)
                        attr.t.CopyFrom(numpy_helper.from_array(new_arr))
                        print(f"Updated node {node.name} from [64, 80] to [64, 35]")

    # Update output shape from [1, 84, 8400] to [1, 39, 8400] (4 box coords + 35 classes)
    for out in onnx_model.graph.output:
        if out.name == "output0":
            out.type.tensor_type.shape.dim[1].dim_value = 39
            print("Updated output0 shape dimension 1 to 39 (35 classes + 4 bbox coords).")

    # Save converted ONNX model
    os.makedirs(os.path.dirname(OUT_ONNX_PATH), exist_ok=True)
    onnx.save(onnx_model, OUT_ONNX_PATH)
    print("Saved converted ONNX model to:", OUT_ONNX_PATH)
    print(f"Model size: {os.path.getsize(OUT_ONNX_PATH) / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    convert()
