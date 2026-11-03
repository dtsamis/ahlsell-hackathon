print("SCRIPT ENTRY")
import io
import zipfile
import pickle
import traceback
import numpy as np

def run():
    try:
        z = zipfile.ZipFile('weights/best.pt')
        data_bytes = z.read('best/data.pkl')

        def read_storage(key, dtype=np.float32):
            raw = z.read(f'best/data/{key}')
            return np.frombuffer(raw, dtype=dtype)

        def rebuild_tensor_v2(storage_info, storage_offset, size, stride, requires_grad, backward_hooks=None):
            tag, s_type, key, device, numel = storage_info
            s_name = getattr(s_type, 'name', str(s_type))
            dtype = np.float32
            if 'Half' in s_name or 'Float16' in s_name:
                dtype = np.float16
            elif 'Double' in s_name or 'Float64' in s_name:
                dtype = np.float64
            elif 'Int' in s_name or 'Long' in s_name:
                dtype = np.int64
            elif 'Byte' in s_name:
                dtype = np.uint8

            storage = read_storage(key, dtype=dtype)
            itemsize = storage.itemsize
            byte_strides = tuple(s * itemsize for s in stride)
            arr = np.lib.stride_tricks.as_strided(storage[storage_offset:], shape=size, strides=byte_strides)
            return np.copy(arr)

        def rebuild_parameter(data, requires_grad=False, backward_hooks=None):
            return data

        class WeightLoader(pickle.Unpickler):
            def find_class(self, module, name):
                if name == '_rebuild_tensor_v2':
                    return rebuild_tensor_v2
                if name == '_rebuild_parameter':
                    return rebuild_parameter
                class Dummy:
                    def __init__(self, *args, **kwargs):
                        self.args = args
                        self.name = name
                    def __setstate__(self, state):
                        self.state = state
                    def __repr__(self):
                        return f'<{self.name}>'
                return Dummy

            def persistent_load(self, pid):
                return pid

        loader = WeightLoader(io.BytesIO(data_bytes))
        obj = loader.load()
        mod = obj['model']
        w = mod.state['_modules']['model'].state['_modules']['0'].state['_modules']['conv'].state['_parameters']['weight']
        print('Successfully extracted conv.weight as numpy array!')
        print('Shape:', w.shape, 'dtype:', w.dtype, 'mean:', float(np.mean(w)), 'std:', float(np.std(w)))
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    run()
