import os
import numpy as np

data_path = "NBA_Player_Stats.tsv"
output_dir = "outputs"
top_n_default = 100

#---------------------------
# Loading and cleaning helpers
#---------------------------

def load_data(path):
    return np.genfromtxt(path, delimiter="\t", names = True, dtype=None)

def to_float(col):
    #Converts a structured column into a float ndarray. Empty strungs become NaN
    col = col.astype(str)
    col = np.where(col == "", "nan", col)
    return col.astype(float)

def safe_divide(numer, denom):
    #Elementwise divide. Returns Nan when denom is 0
    numer = numer.astype(float)
    denom = denom.astype(float)
    return np.where(denom != 0, numer / denom, np.nan)

def top_n_indicies(values, n):
    #Returns indices of the top n values in descending order. NaN values sink to the bottom
    clean = np.where(np.isnan(values), -np.inf, values)
    order = np.argsort(clean)[::-1]
    return order[:n]

#------------------------------
#Metric Calculations
#------------------------------

def compute_metrics(data):
    #Computes all assignment metrics and returns a dictionary. Each metric is a 1D ndarray alligned with the original rows.
    gp = to_float(data["GP"])
    minutes = to_float(data["MIN"])

    fgm = to_float(data["FGM"])
    fga = to_float(data["FGA"])
    tpm = to_float(data["3PM"])
    tpa = to_float(data["3PA"])
    ftm = to_float(data["FTM"])
    fta = to_float(data["FTA"])

    pts = to_float(data["PTS"])
    blk = to_float(data["BLK"])
    stl = to_float(data["STL"])

    fg_acc = safe_divide(fgm, fga)
    tp_acc = safe_divide(tpm, tpa)
    ft_acc = safe_divide(ftm, fta)

    pts_per_min = safe_divide(pts, minutes)
    pts_per_game = safe_divide(pts, gp)

    overall_acc = safe_divide(
        fgm + tpm + ftm,
        fga + tpa + fta
    )

    blk_per_game = safe_divide(blk, gp)
    stl_per_game = safe_divide(stl, gp)

    return {
        "field_goal_accuracy": fg_acc,
        "three_point_accuracy": tp_acc,
        "free_throw_accuracy": ft_acc,
        "points_per_minute": pts_per_min,
        "points_per_game": pts_per_game,
        "overall_shooting_accuracy": overall_acc,
        "blocks_per_game": blk_per_game,
        "steals_per_game": stl_per_game
    }

def metric_display_names():
    return {
        "field_goal_accuracy": "Field Goal Accuracy (FGM / FGA)",
        "three_point_accuracy": "Three Point Accuracy (3PM / 3PA)",
        "free_throw_accuracy": "Free Throw Accuracy (FTM / FTA)",
        "points_per_minute": "Points Per Minute (PTS / MIN)",
        "points_per_game": "Points Per Game (PTS / GP)",
        "overall_shooting_accuracy": "Overall Shooting Accuracy ((FGM+3PM+FTM) / (FGA+3PA+FTA))",
        "blocks_per_game": "Blocks Per Game (BLK / GP)",
        "steals_per_game": "Steals Per Game (STL / GP)"
    }

#-----------------------
#Output Helpers
#-----------------------

def ensure_output_dir():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def save_top_list(filepath, players, seasons, values, indices):
    #Saves a ranked list to a TSV file
    with open(filepath, "w") as f:
        f.write("Rank\tPlayer\tSeason\tValue\n")
        rank = 1
        for i in indices:
            val = values[i]
            if np.isnan(val):
                continue
            f.write(f"{rank}\t{players[i]}\t{seasons[i]}\t{val:.6f}\n")
            rank += 1

def preview_top_list(title, players, seasons, values, indices, preview_count = 10):
    print()
    print(title)
    print("Rank | Player | Season | Value")
    shown = 0
    rank = 1
    for i in indices:
        val = values[i]
        if np.isnan(val):
            continue
        print(f"{rank} | {players[i]} | {seasons[i]} | {val:.4f}")
        shown += 1
        rank += 1
        if shown >= preview_count:
            break

#---------------------------
#Menu and Program Flow
#---------------------------

def print_menu():
    print("\nNBA NumPy Analyzer")
    print("1) Preview Top 10 for a metric")
    print("2) Save Top 100 files for all metrics")
    print("3) Save Top N files for all metrics (choose N)")
    print("4) Quit\n")
    print()

def choose_metric_key(keys, display_map):
    print()
    print("Choose a metric:")
    for i, key in enumerate(keys, start=1):
        print(f"{i}) {display_map[key]}")
    print()

    choice = input("Enter a number: ").strip()
    if not choice.isdigit():
        return None
    num = int(choice)
    if num < 1 or num > len(keys):
        return None
    return keys[num - 1]

def run_preview(data, metrics):
    players = data["Player"].astype(str)
    seasons = data["Season"].astype(str)

    display_map = metric_display_names()
    keys = list(metrics.keys())

    metric_key = choose_metric_key(keys, display_map)
    if metric_key is None:
        print("Invalid choice")
        return
    
    values = metrics[metric_key]
    top_idx = top_n_indicies(values, 100)
    preview_top_list(display_map[metric_key], players, seasons, values, top_idx, preview_count=10)

def run_save_all(data, metrics, n):
    ensure_output_dir()
    
    players = data["Player"].astype(str)
    seasons = data["Season"].astype(str)
    display_map = metric_display_names()

    print()
    print(f"Saving Top {n} files to the '{output_dir}' folder...")

    for key, values in metrics.items():
        idx = top_n_indicies(values, n)
        filepath = os.path.join(output_dir, f"top_{n}_{key}.tsv")
        save_top_list(filepath, players, seasons, values, idx)
        print(f"Saved: {filepath}")
    
    print("Done")

def get_top_n_from_user():
    raw = input(f"Enter N (example: {top_n_default}): ").strip()
    if not raw.isdigit():
        return None
    n = int(raw)
    if n <= 0:
        return None
    return n
    
def main():
    if not os.path.exists(data_path):
        print(f"Could not find {data_path}. Put it in the same folder as the script.")
        return
        
    data = load_data(data_path)
    metrics = compute_metrics(data)

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            run_preview(data, metrics)
        elif choice == "2":
            run_save_all(data, metrics, top_n_default)
        elif choice == "3":
            n = get_top_n_from_user()
            if n is None:
                print("Invalid N")
            else:
                run_save_all(data, metrics, n)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
