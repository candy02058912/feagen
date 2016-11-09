import os.path

import h5py
from mkdir_p import mkdir_p
import six


class FeatureGeneratorType(type):

    def __new__(mcs, clsname, bases, dct):
        # pylint: disable=protected-access

        func_set_dict = {
            'features': {},
            'intermediate_data': {},
        }

        # register the data name
        for attr_key, val in six.viewitems(dct):
            if not hasattr(val, '_feagen_data_type'):
                continue
            set_name = val._feagen_data_type
            func_dict = func_set_dict[set_name]
            for key in val._feagen_will_generate_keys:
                if key in func_dict:
                    raise ValueError("duplicated {} {} in {} and {}".format(
                        set_name, key, func_dict[key], attr_key))
                func_dict[key] = attr_key

        dct['_feature_func_dict'] = func_set_dict['features']
        dct['_intermediate_data_func_dict'] = func_set_dict['intermediate_data']

        return super(FeatureGeneratorType, mcs).__new__(
            mcs, clsname, bases, dct)


class FeatureGenerator(six.with_metaclass(FeatureGeneratorType, object)):

    def __init__(self, global_feature_hdf_path):
        self.intermediate_data = {}
        global_feature_hdf_dir = os.path.dirname(global_feature_hdf_path)
        if global_feature_hdf_dir != '':
            mkdir_p(global_feature_hdf_dir)
        self.global_feature_h5f = h5py.File(global_feature_hdf_path, 'a')

    def generate(self, feature_names):
        if isinstance(feature_names, str):
            feature_names = [feature_names]
        self.require(feature_names, self._feature_func_dict)

    def require(self, keys, func_dict):
        for key in keys:
            getattr(self, func_dict[key])(key)