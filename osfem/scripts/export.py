import sys; sys.path += [".."]
from osfem.general import dict_to_csv
from osfem.data import get_creep

data_list = get_creep("data")
cal_dict = {}
val_dict = {}
for key in data_list[0].keys():
    cal_dict[key] = [data[key] for data in data_list if data["fit"]]
    val_dict[key] = [data[key] for data in data_list if not data["fit"]]
dict_to_csv(cal_dict, "cal_cbc.csv")
dict_to_csv(val_dict, "val_cbc.csv")
