# 第5章 图形界面 (GUI)

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalculate_gui/app.py` (652 行), `pyqalculate_gui/` 目录

---

## 5.1 启动方式

```bash
# 直接启动
python -m pyqalculate_gui

# 通过启动器
start.bat → 选择 [2]
```

**Venv 完整性检查**: 如果安装被中断，启动时会自动重新创建虚拟环境。

[来源: pyqalculate_gui/__main__.py:2]

---

## 5.2 窗口布局

**默认大小**: 800×600 [来源: app.py:85]  
**最小大小**: 600×400 [来源: app.py:86]  
**标题**: "PyQalculate" [来源: app.py:84]

### Component Hierarchy

```
root (tk.Tk)
├── MenuBar                    # Menu bar
└── main (ttk.Frame)
    ├── ResultView             # Result display (fills remaining space)
    ├── ExpressionEdit         # Expression input
    │   └── AutoComplete       # Autocomplete popup (child of ExpressionEdit)
    ├── ExpressionStatusBar    # Expression status
    ├── KeypadWidget           # Virtual keypad
    └── StatusBar              # Bottom status bar
```

**Notes**:
- HistoryView is created but not packed (backend only, used by answer(N) and history window)
- ConversionView opens as a separate Toplevel window (not in main)
- PanedWindow does NOT exist in the widget tree

[来源: app.py:131-204]

---

## 5.3 核心组件

### ExpressionEdit — 表达式输入

- 多行 `tk.Text` 组件，自动换行 [来源: expression_edit.py:22-183]
- Enter 键提交表达式 [来源: expression_edit.py:68-80]
- 手动撤销/重做（最多 100 步）[来源: expression_edit.py:19, 42-43]
- 公共 API: `get_expression()`, `set_expression()`, `insert_at_cursor()`, `clear()`, `undo()`, `redo()` [来源: expression_edit.py:100-168]

### ResultView — Result Display

- Read-only `tk.Text` component [来源: result_view.py:26-176]
- Text labels: `expression`, `result`, `approx`, `error`, `separator`, `info` [来源: result_view.py:74-91]
- Math rendering: Uses `MathRenderer` to convert to matplotlib math text [来源: result_view.py:107-113]
- **Double-click recall**: Double-clicking on a result recalls the expression to the input field [来源: result_view.py]

### KeypadWidget — Virtual Keypad

6 rows × 5 columns button grid [来源: keypad.py:79-180]:

| Row | Col 0 | Col 1 | Col 2 | Col 3 | Col 4 |
|-----|-------|-------|-------|-------|-------|
| 0 | sin | cos | tan | ln | log |
| 1 | ( | ) | x² | xʸ | √ |
| 2 | 7 | 8 | 9 | DEL | AC |
| 3 | 4 | 5 | 6 | × | ÷ |
| 4 | 1 | 2 | 3 | + | − |
| 5 | 0 | . | EXP | ± | = |

**Dropdown Menus**: Right-click on function buttons to access alternatives:
- `sin` → asin, sinh, asinh
- `cos` → acos, cosh, acosh
- `tan` → atan, tanh, atanh
- `√` → ∛ (cbrt)
- `ln` → log, log₂, log₁₀
- `log` → log₂, log₁₀
- `x²` → x³
- `xʸ` → x^(1/y)

[来源: keypad.py:15-96]

### HistoryView — History Display

- Single instance (removed duplicate HistoryView)
- Scrollable `tk.Listbox` [来源: history_view.py:37-168]
- Shows expressions, results, errors
- **Double-click recall**: Double-clicking recalls expression to input [来源: history_view.py:85-97]
- `answer(N)` support: `get_answer(n)` returns the N-th most recent result [来源: history_view.py:144-149]

### ConversionView — 单位转换

双面板布局 [来源: conversion_view.py:28-458]:
- 左侧: 分类树 + 单位列表
- 右侧: 搜索栏 + 值输入 + 转换按钮
- 自动转换 [来源: conversion_view.py:360-363]

### StatusBar — Status Bar

- Left: "Functions: N | Units: N | Variables: N" [来源: status_bar.py:30-31]
- Right: "Exact" or "Approximate" mode indicator [来源: status_bar.py:38]
- **= vs ≈ display**: Exact results show "=" prefix, approximate results show "≈" prefix

### ExpressionStatusBar — 表达式状态

- 左侧: 解析后的表达式、函数提示、错误 [来源: expression_status.py:97-133]
- 右侧: 模式指示器徽章 [来源: expression_status.py:144-183]
  - EXACT, RPN, CHN, BIN/OCT/HEX/DUO, DEG/RAD/GRA, FUNC, UNIT, VAR

---

## 5.4 菜单栏

[来源: menu_bar.py:24-120]

### File 菜单

| 菜单项 | 快捷键 | 功能 |
|--------|--------|------|
| Import CSV... | — | 导入 CSV |
| Export CSV... | — | 导出 CSV |
| Preferences... | — | 打开设置 |
| Exit | — | 退出 |

[来源: menu_bar.py:53-60]

### Edit 菜单

| 菜单项 | 快捷键 | 功能 |
|--------|--------|------|
| Copy Result | Ctrl+C | 复制结果 |
| Clear Expression | — | 清除表达式 |
| Clear All | Ctrl+L | 清除所有 |

[来源: menu_bar.py:62-71]

### Mode 菜单

| 菜单项 | 功能 |
|--------|------|
| Exact Mode | 切换精确模式 |
| Functions... | 管理函数 |
| Variables... | 管理变量 |
| Units... | 管理单位 |

[来源: menu_bar.py:73-80]

### Tools 菜单

| 菜单项 | 功能 |
|--------|------|
| Plot... | 打开绘图对话框 |
| Curve Fitting... | 打开曲线拟合对话框 |
| Number Bases... | 打开进制转换 |
| Unit Conversion... | 打开单位转换窗口 |
| History... | 打开历史窗口 |

[来源: menu_bar.py:82-92]

### Help 菜单

| 菜单项 | 功能 |
|--------|------|
| Help Documentation | 打开帮助 |
| About | 显示关于对话框 |

[来源: menu_bar.py:90-95]

---

## 5.5 键盘快捷键

[来源: keyboard_shortcuts.py:169-215]

| 快捷键 | 功能 | 常量 |
|--------|------|------|
| Ctrl+Q | 退出 | `QUIT` |
| F1 | 帮助 | `HELP` |
| Ctrl+B | 进制转换 | `NUMBER_BASES` |
| Ctrl+Alt+C | 复制结果 | `COPY_RESULT` |
| Ctrl+S | 存储结果 | `STORE` |
| Ctrl+M | 管理变量 | `MANAGE_VARIABLES` |
| Ctrl+F | 管理函数 | `MANAGE_FUNCTIONS` |
| Ctrl+U | 管理单位 | `MANAGE_UNITS` |
| Ctrl+K / Alt+K | 切换键盘 | `KEYPAD` |
| Ctrl+H / Alt+H | 切换历史 | `HISTORY` |
| Ctrl+Space | 切换最小模式 | `MINIMAL` |
| Ctrl+O / Alt+O | 切换转换面板 | `CONVERSION` |
| Ctrl+T | 转换到单位 | `CONVERT` |
| Ctrl+P | 切换编程键盘 | `PROGRAMMING` |
| Ctrl+R | 切换 RPN 模式 | `RPN_MODE` |
| Tab | 接受第一个补全 | `ACTIVATE_FIRST_COMPLETION` |
| Ctrl+Shift+( | 插入括号 | `PARENTHESES` |
| Ctrl+Shift+) | 插入括号 | `PARENTHESES` |

**RPN 快捷键**:

| 快捷键 | 功能 |
|--------|------|
| Ctrl+Up | RPN: 上移栈 |
| Ctrl+Down | RPN: 下移栈 |
| Ctrl+Right | RPN: 交换顶部两项 |
| Ctrl+Left | RPN: 召回 last x |
| Ctrl+Shift+C | RPN: 复制顶部 |
| Ctrl+Delete | RPN: 删除顶部 |
| Ctrl+Shift+Delete | RPN: 清空栈 |

---

## 5.6 主题系统

两个内置主题 [来源: theme.py:1-102]:

| 主题 | 说明 |
|------|------|
| `LIGHT` | 亮色主题（默认） |
| `DARK` | 暗色主题 |

**切换方式**: Preferences → Appearance → Theme [来源: preferences_dialog.py:260-316]

**主题包含**:
- 颜色: bg, fg, entry_bg, select_bg, expression_fg, result_fg, error_fg 等 [来源: theme.py:20-33]
- 字体: expression_font, result_font, info_font [来源: theme.py:35-38]
- 按钮样式: keypad_digit, keypad_op, keypad_func 等 [来源: theme.py:40-47]

---

## 5.7 对话框

### Preferences — 设置对话框

三个选项卡 [来源: preferences_dialog.py:50-337]:

**Calculation 选项卡**:
- Precision: 1-100（默认 8）
- Approximation: Exact / Try Exact / Approximate
- Angle Unit: none / radians / degrees / gradians

**Display 选项卡**:
- Number Format: Decimal / Scientific / Engineering
- Digit Grouping: 开/关
- Unicode Signs: 开/关
- Exponent Display: default / uppercase_e / lowercase_e / power_of_10

**Appearance 选项卡**:
- Font Family: Consolas, Courier New, Cascadia Code 等
- Font Size: 8-24（默认 11）
- Theme: Light / Dark

设置保存到 `~/.pyqalculate/preferences.json` [来源: preferences_dialog.py:24-25]

### Plot — 绘图对话框

大小: 900×680 [来源: plot_dialog.py:41]

- 左侧: 表达式列表、X 范围、样式选项
- 右侧: matplotlib 画布 + 工具栏
- 支持多表达式（10 色调色板）[来源: plot_dialog.py:25-28]
- 保存为 PNG 或 SVG [来源: plot_dialog.py:491-537]

### Curve Fitting — 曲线拟合对话框

**菜单路径**: Tools → Curve Fitting...

**功能**: 输入 X/Y 数据点，选择拟合类型（线性/二次/三次），计算并可视化回归结果。

**使用步骤**:
1. 在 X values / Y values 输入框中输入数据（逗号或空格分隔）
2. 选择拟合类型（Linear / Quadratic / Cubic）
3. 点击 **Fit** 按钮
4. 查看多项式表达式和 matplotlib 图表（散点 + 拟合曲线）
5. 可选：点击 **Insert to Expression** 将结果插入主窗口

**结果格式**: 返回以 x 表示的多项式，例如 `0.7797619*(x)^2 - 4.7202381*x + 9.7321429`

### Number Bases — 进制转换对话框

同时显示六种进制 [来源: dialogs/number_bases.py:31-225]:
- 十进制、二进制 (0b)、八进制 (0o)、十六进制 (0x)
- 十二进制（Dozenal Society 字符）
- 罗马数字

### Functions List — 函数列表对话框

- 可搜索函数列表 [来源: dialogs/functions_list.py:17-182]
- 显示名称、描述、分类、参数数量
- "Insert into Expression" 按钮

### Import/Export CSV — CSV 导入/导出

**导入** [来源: import_csv_dialog.py:19-230]:
- 文件路径浏览
- 变量名（自动从文件名填充）
- 分隔符选择: Comma / Tab / Semicolon / Space / Other
- 输出格式: 按列分离向量 / 单一矩阵变量

**导出** [来源: export_csv_dialog.py:27-217]:
- 数据源: 命名变量 / 当前结果
- 分隔符选择

---

## 5.X 国际化 (i18n)

[来源: i18n.py:1-122]

PyQalculate GUI 支持通过 gettext 实现多语言界面。当前支持：

| 语言 | 代码 | 翻译文件 |
|------|------|---------|
| English | en | (默认) |
| 中文（简体） | zh_CN | `locales/zh_CN/LC_MESSAGES/pyqalculate.po` |

**切换方式**: Preferences → Appearance → Language（需重启生效）

**翻译覆盖**: 菜单栏、对话框、按钮、状态栏、快捷键说明等 UI 文本。

---

## 5.8 自动补全

[来源: autocomplete.py:54-330]

- 弹出 `Toplevel` 显示匹配项
- 评分算法: 6=精确匹配, 5=名称开头, 4=标题开头, 3=名称包含, 2=标题包含 [来源: autocomplete.py:25-51]
- 最多 20 个可见项 [来源: autocomplete.py:23]
- 键盘: Up/Down 导航, Tab/Enter 接受, Escape 隐藏 [来源: app.py:517-540]
