import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from math import pi

# --- 设置中文字体与风格 ---
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')

# 创建画布：1行2列
fig = plt.figure(figsize=(18, 8), dpi=150)

# ==============================================================================
# 左图：VisDrone 数据集上的 效率-精度 散点图 (结合表 5-4 和 5-5)
# ==============================================================================
ax1 = fig.add_subplot(1, 2, 1)

# 数据格式: [模型名称, Params(M), mAP@.5%, GFLOPs, 类型(颜色组)]
# 类型: 0=TDA-YOLO, 1=YOLO通用系列, 2=UAV专用系列
scatter_data = [
    # --- 核心模型 ---
    ["TDA-YOLO",       2.6,  48.4, 7.9,  0],
    
    # --- YOLO 系列 (表 5-4) ---
    ["YOLOv11-n",      2.6,  30.2, 6.3,  1],
    ["YOLOv11-s",      9.4,  36.4, 21.3, 1],
    ["YOLOv9-e",       57.4, 46.6, 189.2,1], # 大模型对比
    ["YOLOv8-n",       3.0,  32.6, 8.1,  1],
    ["YOLOv8-s",       11.1, 38.5, 28.5, 1],
    ["YOLOv8-m",       25.8, 41.7, 78.9, 1],
    ["YOLOv8-l",       43.6, 43.0, 165.2,1],
    ["YOLOv7",         36.9, 37.9, 104.7,1],
    ["YOLOv5-s",       9.1,  46.2, 23.8, 1],
    ["YOLOv5-n",       2.5,  31.8, 7.1,  1],
    
    # --- UAV 系列 (表 5-5) ---
    ["ACAM-YOLO",      15.9, 47.8, 52.1, 2],
    ["Edge-YOLO",      40.5, 44.8, 60.0, 2], # GFLOPs估算
    ["UAV-YOLOv8",     10.3, 47.0, 25.0, 2], # GFLOPs估算
    ["PVswin-YOLO",    41.8, 43.3, 80.0, 2],
    ["Drone-YOLO-n",   3.1,  38.1, 8.0,  2],
    ["Modified YOLOv8",9.66, 42.2, 25.0, 2],
]

# 提取绘图数据
for name, param, map_val, gflops, type_idx in scatter_data:
    # 颜色与形状定义
    if type_idx == 0: # Ours
        color = '#FF0000'
        marker = '*'
        size = 600
        alpha = 1.0
        edgecolor = 'black'
        zorder = 100
        font_weight = 'bold'
        fontsize = 12
    elif type_idx == 1: # YOLO Series
        color = '#808080' # 灰色
        marker = 'o'
        size = gflops * 8 + 50 # 气泡大小基于 GFLOPs
        alpha = 0.6
        edgecolor = 'white'
        zorder = 5
        font_weight = 'normal'
        fontsize = 9
    else: # UAV Series
        color = '#4682B4' # 钢蓝色
        marker = 'D' # 菱形
        size = gflops * 6 + 50
        alpha = 0.7
        edgecolor = 'white'
        zorder = 10
        font_weight = 'normal'
        fontsize = 9

    # 绘制点
    ax1.scatter(param, map_val, s=size, c=color, marker=marker, 
                edgecolors=edgecolor, alpha=alpha, zorder=zorder, linewidth=1)
    
    # 添加标签 (避让逻辑简化版)
    offset_y = 0.6
    offset_x = 0
    if name == "TDA-YOLO": 
        offset_y = 1.0
        t = ax1.text(param, map_val + offset_y, name + "\n(Ours)", color='#D50000', 
                 fontsize=14, fontweight='bold', ha='center', va='bottom', zorder=101)
    elif name in ["YOLOv11-n", "YOLOv9-e", "ACAM-YOLO", "YOLOv5-s", "YOLOv8-m"]:
        # 只标注关键对比模型，避免拥挤
        if "ACAM" in name: offset_y = -1.5
        if "YOLOv11-n" in name: offset_y = -1.8
        t = ax1.text(param + offset_x, map_val + offset_y, name, color='black', 
                 fontsize=fontsize, fontweight=font_weight, ha='center', va='bottom', zorder=20)

# 装饰左图
ax1.set_xlabel("参数量 Parameters (M) → (越小越好)", fontsize=12, fontweight='bold')
ax1.set_ylabel("VisDrone mAP@.5% ↑ (越高越好)", fontsize=12, fontweight='bold')
ax1.set_title("VisDrone 数据集：模型效率与精度全景对比\n(气泡大小代表计算量 GFLOPs)", fontsize=14, fontweight='bold', pad=20)
ax1.grid(True, linestyle='--', alpha=0.4)
ax1.set_xlim(0, 65) # 限制X轴以突出轻量级区域
ax1.set_ylim(20, 52)

# 添加帕累托最优区域注释
ax1.add_patch(mpatches.FancyArrowPatch((10, 30), (2.8, 47), connectionstyle="arc3,rad=.2", 
                                       arrowstyle="Simple, tail_width=0.5, head_width=4, head_length=4", color='orange', alpha=0.5))
ax1.text(12, 28, "TDA-YOLO 实现极低参数下的最高精度", color='orange', fontsize=11, fontweight='bold')


# ==============================================================================
# 右图：六维能力雷达图 (综合 Table 5-4, 5-6)
# ==============================================================================
ax2 = fig.add_subplot(1, 2, 2, polar=True)

# 维度定义
categories = [
    'VisDrone\nmAP@.5%', 
    'DOTAv2\nmAP@.5%', 
    'VisDrone\n精准率 (Precision)', 
    'DOTAv2\nF1-Score',
    '参数效率\n(1/Params)',    # 倒数，越大越好
    '计算效率\n(1/GFLOPs)'     # 倒数，越大越好
]
N = len(categories)

# 数据准备 (归一化处理以便于雷达图展示)
# 原始数据: [Vis_mAP, DOTA_mAP, Vis_Prec, DOTA_F1, Params, GFLOPs]
# TDA-YOLO: [48.4, 48.6, 75.5, 51.3, 2.6, 7.9]
# YOLOv11-n: [30.2, 28.6, 40.2, 38.5, 2.6, 6.3] (Table 5-4 & 5-6)
# YOLOv8-n:  [32.6, 30.7, 43.2, 35.8, 3.0, 8.1] (Table 5-4 & 5-6)
# ACAM-YOLO: [47.8, 35.0(估), 60.0(估), 40.0(估), 15.9, 52.1] (Table 5-5 & 假设) -> 替换为 YOLOv8-m 以保证数据准确
# 决定对比: TDA-YOLO vs YOLOv11-n vs YOLOv8-n (同量级最强对比)

raw_data = {
    "TDA-YOLO (Ours)": [48.4, 48.6, 75.5, 51.3, 2.6, 7.9],
    "YOLOv11-n":       [30.2, 28.6, 40.2, 38.5, 2.6, 6.3],
    "YOLOv8-n":        [32.6, 30.7, 43.2, 35.8, 3.0, 8.1]
}

# 归一化函数 (Min-Max Scaling 到 0.2-1.0 之间，避免重叠)
def normalize(val, min_v, max_v, inverted=False):
    if inverted: # 对于Params和GFLOPs，越小越好 -> 倒数归一化
        score = (min_v / val) 
    else:
        score = (val) / max_v
    return score

# 计算绘图数据
plot_data = {}
# 手动设置各维度的参考最大/最小值以进行归一化
max_vals = [50, 50, 80, 55] # 前4个指标的上限
# 后两个指标通过比较倒数或直接相对值计算
for name, values in raw_data.items():
    scores = []
    scores.append(values[0] / 55) # Vis mAP
    scores.append(values[1] / 55) # DOTA mAP
    scores.append(values[2] / 80) # Precision
    scores.append(values[3] / 55) # F1
    # 参数效率: 以 2.5M 为基准 (分数 = 2.5 / 实际参数)
    scores.append(min(1.0, 2.5 / values[4])) 
    # 计算效率: 以 6.0G 为基准
    scores.append(min(1.0, 6.0 / values[5]))
    
    plot_data[name] = scores

# 角度计算
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

# 绘制雷达
colors = {'TDA-YOLO (Ours)': '#FF0000', 'YOLOv11-n': '#2E8B57', 'YOLOv8-n': '#4682B4'}
styles = {'TDA-YOLO (Ours)': '-', 'YOLOv11-n': '--', 'YOLOv8-n': ':'}

for name, values in plot_data.items():
    values += values[:1] # 闭合
    ax2.plot(angles, values, linewidth=2, linestyle=styles[name], label=name, color=colors[name])
    ax2.fill(angles, values, color=colors[name], alpha=0.15)

# 设置标签
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, fontsize=11, fontweight='bold', color='#333333')
ax2.set_yticklabels([]) # 隐藏径向刻度
ax2.set_ylim(0, 1.05)

# 添加特定数值标注 (在雷达图顶点显示 TDA-YOLO 的真实数值)
tda_vals = raw_data["TDA-YOLO (Ours)"]
# VisDrone mAP
ax2.text(angles[0], plot_data["TDA-YOLO (Ours)"][0]+0.1, f"48.4%\n(Top 1)", ha='center', color='red', fontweight='bold')
# DOTA mAP
ax2.text(angles[1], plot_data["TDA-YOLO (Ours)"][1]+0.15, f"48.6%\n(+20%)", ha='right', color='red', fontweight='bold')

ax2.set_title("综合性能对比：TDA-YOLO vs 主流轻量级模型\n(覆盖 VisDrone 与 DOTAv2 双数据集)", fontsize=14, fontweight='bold', pad=30)
ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10, frameon=True, shadow=True)

# 调整布局
plt.tight_layout()
plt.subplots_adjust(wspace=0.15)
plt.show()