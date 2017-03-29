import hashlib


file_list = [
    "client/dat/Item.dat",
    "client/dat/ND/NDItem.dat",
    "server/Script/FaceItem.dat",
    "server/Script/FaceItem_str.dat",
    "server/Script/UpperItem.dat",
    "server/Script/UpperItem_str.dat",
    "server/Script/LowerItem.dat",
    "server/Script/LowerItem_str.dat",
    "server/Script/GauntletItem.dat",
    "server/Script/GauntletItem_str.dat",
    "server/Script/ShoeItem.dat",
    "server/Script/ShoeItem_str.dat",
    "server/Script/HelmetItem.dat",
    "server/Script/HelmetItem_str.dat",
    "server/Script/WeaponItem.dat",
    "server/Script/WeaponItem_str.dat",
    "server/Script/shielDItem.dat",
    "server/Script/shielDItem_str.dat",
    "server/Script/cloaKItem.dat",
    "server/Script/cloaKItem_str.dat",
    "server/Script/rIngItem.dat",
    "server/Script/rIngItem_str.dat",
    "server/Script/AmuletItem.dat",
    "server/Script/AmuletItem_str.dat",
    "server/Script/BulletItem.dat",
    "server/Script/BulletItem_str.dat",
    "server/Script/MakeToolItem.dat",
    "server/Script/MakeToolItem_str.dat",
    "server/Script/PotionItem.dat",
    "server/Script/PotionItem_str.dat",
    "server/Script/bagItem.dat",
    "server/Script/bagItem_str.dat",
    "server/Script/baTteryItem.dat",
    "server/Script/baTteryItem_str.dat",
    "server/Script/OreItem.dat",
    "server/Script/OreItem_str.dat",
    "server/Script/ResourceItem.dat",
    "server/Script/ResourceItem_str.dat",
    "server/Script/forCeItem.dat",
    "server/Script/forCeItem_str.dat",
    "server/Script/UnitkeyItem.dat",
    "server/Script/UnitFrame.dat",
    "server/Script/UnitkeyItem_str.dat",
    "server/Script/bootYItem.dat",
    "server/Script/bootYItem_str.dat",
    "server/Script/MAPItem.dat",
    "server/Script/MAPItem_str.dat",
    "server/Script/TOWNItem.dat",
    "server/Script/TOWNItem_str.dat",
    "server/Script/BattleDungeonItem.dat",
    "server/Script/BattleDungeonItem_str.dat",
    "server/Script/AnimusItem.dat",
    "server/Script/AnimusItem_str.dat",
    "server/Script/GuardTowerItem.dat",
    "server/Script/GuardTowerItem_str.dat",
    "server/Script/TrapItem.dat",
    "server/Script/TrapItem_str.dat",
    "server/Script/SiegeKitItem.dat",
    "server/Script/SiegeKitItem_str.dat",
    "server/Script/TicketItem.dat",
    "server/Script/TicketItem_str.dat",
    "server/Script/EventItem.dat",
    "server/Script/EventItem_str.dat",
    "server/Script/RecoveryItem.dat",
    "server/Script/RecoveryItem_str.dat",
    "server/Script/BoxItem.dat",
    "server/Script/BoxItem_str.dat",
    "server/Script/Firecracker.dat",
    "server/Script/Firecracker_str.dat",
    "server/Script/UNmannedminer.dat",
    "server/Script/UNmannedminer_str.dat",
    "server/Script/RadarItem.dat",
    "server/Script/RadarItem_str.dat",
    "server/Script/NPCLinkItem.dat",
    "server/Script/NPCLinkItem_str.dat",
    "server/Script/CouponItem.dat",
    "server/Script/CouponItem_str.dat",
    "server/Script/UnitHead.dat",
    "server/Script/UnitHead_str.dat",
    "server/Script/UnitUpper.dat",
    "server/Script/UnitUpper_str.dat",
    "server/Script/UnitLower.dat",
    "server/Script/UnitLower_str.dat",
    "server/Script/UnitArms.dat",
    "server/Script/UnitArms_str.dat",
    "server/Script/UnitShoulder.dat",
    "server/Script/UnitShoulder_str.dat",
    "server/Script/UnitBack.dat",
    "server/Script/UnitBack_str.dat",
    "server/Script/UnitBullet.dat",
    "server/Script/UnitBullet_str.dat",
    "server/Script/ItemMakeData.dat",
    "server/Script/ItemCombine.dat"
]
not_same = []


for file in file_list:
    f1 = open("./dat_files/GU/" + file, "rb")
    f2 = open("./dat_files/src/" + file, "rb")

    data1 = f1.read()
    data2 = f2.read()

    hash1 = hashlib.md5()
    hash1.update(data1)
    hash1 = hash1.hexdigest()

    hash2 = hashlib.md5()
    hash2.update(data2)
    hash2 = hash2.hexdigest()

    if hash1 != hash2:
        not_same.append(file)

    f1.close()
    f2.close()

if len(not_same) == 0:
    print("All files is same!")
else:
    print("Different files ({}):".format(len(not_same)))
    for file in not_same:
        print(file)
