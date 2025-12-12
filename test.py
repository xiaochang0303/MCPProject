from tourmcp import get_spots_by_province, get_spots_by_city
import json

def print_json(title, data):
    print(f"\n=== {title} ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    # 测试省份读取
    province = "浙江"
    # print(f"测试从省份 '{province}' 读取景点数据:")
    # result_province = get_spots_by_province(province)
    # print_json("省份数据", result_province)

    # 测试城市读取
    city = "舟山"
    print(f"\n测试从城市 '{province}/{city}' 读取景点数据:")
    result_city = get_spots_by_city(province, city)
    print_json("城市数据", result_city)


if __name__ == "__main__":
    main()