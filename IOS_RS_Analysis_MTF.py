import os
import fnmatch
import pandas as pd
import matplotlib.pyplot as plt


def find_matching_files(keyword):
    target_dir = os.path.join(os.getcwd(), "Vadav_Cal", "MTF")

    if not os.path.exists(target_dir):
        print(f"폴더가 존재하지 않습니다: {target_dir}")
        return []

    matching_files = []
    for file in os.listdir(target_dir):
        if fnmatch.fnmatch(file, f"*{keyword}*MTF*.txt"):
            matching_files.append(os.path.join(target_dir, file))

    # 자연수 기준으로 정렬 (예: 1, 2, ..., 10)
    def extract_number(path):
        basename = os.path.basename(path)
        try:
            number = int(basename.split(keyword)[0].strip())
        except ValueError:
            number = float('inf')  # 숫자 추출 안 되면 뒤로 보냄
        return number

    matching_files.sort(key=extract_number)
    return matching_files


def load_mtf_data(files, keyword):
    data_frames = {}
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 1/mm MTF 데이터를 찾기
        data_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith("1/mm"):
                data_start = i + 1
                break

        if data_start is None:
            continue

        # 데이터 읽기
        data = []
        for line in lines[data_start:]:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    data.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    continue

        # 데이터프레임 생성
        df = pd.DataFrame(data, columns=["1/mm", "MTF"])
        file_time = os.path.basename(file).split(keyword)[0].strip()
        data_frames[f"{file_time}{keyword}"] = df

    return data_frames


def plot_mtf_data(data_frames, filename, odd_only=False):
    plt.figure(figsize=(8, 6))

    max_x = 0
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    for i, (time, df) in enumerate(data_frames.items()):
        try:
            num = int(''.join(filter(str.isdigit, time)))
            if odd_only and num % 2 == 0:
                continue  # 홀수만 원할 경우 짝수는 건너뜀
        except ValueError:
            continue  # 숫자 추출 실패 시 스킵

        color = colors[i % len(colors)]
        plt.plot(df["1/mm"], df["MTF"], label=time, color=color)
        max_x = max(max_x, df["1/mm"].max())

        for x_val in [10, 20]:
            mtf_value = df.loc[df["1/mm"].sub(x_val).abs().idxmin()]
            plt.scatter(mtf_value["1/mm"], mtf_value["MTF"], marker='o', color=color)
            plt.text(mtf_value["1/mm"], mtf_value["MTF"] + 0.02,
                     f"{mtf_value['MTF']:.3f}", ha='center', fontsize=10, color=color)

    plt.axvline(x=10, color='gray', linestyle='--')
    plt.axvline(x=20, color='gray', linestyle='--')

    plt.xlabel("1/mm")
    plt.ylabel("MTF")
    plt.title("MTF vs Spatial Frequency" + (" (Odd Only)" if odd_only else ""))
    plt.legend()
    plt.grid(True)

    plt.xlim(0, max_x)
    plt.ylim(0, 1)

    target_dir = os.path.join(os.getcwd(), "Vadav_Cal", "MTF")
    save_path = os.path.join(target_dir, filename + "_freq.png")
    plt.savefig(save_path, format='png')
    plt.show()
    print(f"그래프가 {save_path} 파일로 저장되었습니다.")

def plot_mtf_vs_v(data_frames, filename, keyword):
    if not data_frames:
        return

    plt.figure(figsize=(8, 6))

    v_values = []
    mtf_10_values = []
    mtf_20_values = []

    # ✅ 숫자 기준으로 key 정렬
    def extract_number(label):
        try:
            number = int(''.join(filter(str.isdigit, label)))
        except ValueError:
            number = float('inf')
        return number

    sorted_items = sorted(data_frames.items(), key=lambda x: extract_number(x[0]))

    for time, df in sorted_items:
        v_label = time.replace("_", ".")  # 예: 3min → 3.min → float 가능
        v_values.append(float(v_label.replace(keyword, "").strip()))
        mtf_10 = df.loc[df["1/mm"].sub(10).abs().idxmin(), "MTF"]
        mtf_20 = df.loc[df["1/mm"].sub(20).abs().idxmin(), "MTF"]
        mtf_10_values.append(mtf_10)
        mtf_20_values.append(mtf_20)

    plt.plot(v_values, mtf_10_values, marker='o', label=f"MTF @ 10 1/mm")
    plt.plot(v_values, mtf_20_values, marker='s', label=f"MTF @ 20 1/mm")

    plt.xlabel(keyword)
    plt.ylabel("MTF")
    plt.title(f"MTF @ 10 and 20 1/mm vs {keyword}")
    plt.ylim(0, 0.7)
    plt.xticks(v_values, [f"{v:.1f}{keyword}" for v in v_values], rotation=45)
    plt.legend()
    plt.grid(True)

    save_path = os.path.join(os.getcwd(), "Vadav_Cal", "MTF", filename + f"_{keyword}.png")
    plt.savefig(save_path, format='png')
    plt.show()
    print(f"그래프가 {save_path} 파일로 저장되었습니다.")


if __name__ == "__main__":
    keyword = input("파일에서 사용할 키워드(min, V 또는 th)를 입력하세요: ")
    files = find_matching_files(keyword)
    if files:
        data_frames = load_mtf_data(files, keyword)
        filename = input("저장할 파일 이름을 입력하세요 (확장자 제외): ")

        odd_only_input = input("홀수 파일만 플롯할까요? (yes/no): ").strip().lower()
        odd_only = odd_only_input == "yes"

        plot_mtf_data(data_frames, filename, odd_only)

        if keyword in ["V", "th", "min", "st"]:
            plot_mtf_vs_v(data_frames, filename, keyword)
    else:
        print("조건에 맞는 파일이 없습니다.")