# EvoLabeler 构建指南

## 🎯 快速构建

### 方法 1: 使用自动化脚本（推荐）

```bash
cd evolauncher-frontend/scripts
./build-app.sh
```

### 方法 2: 使用 npm 命令

```bash
cd evolauncher-frontend

# 构建 macOS 应用
npm run build:mac

# 或者使用通用构建命令
npm run build:electron
```

---

## 📋 构建前准备

### 1. 系统要求

- **操作系统**: macOS 10.13+
- **Node.js**: 18.x 或更高
- **npm**: 9.x 或更高
- **磁盘空间**: 至少 2GB 可用空间

### 2. 安装依赖

```bash
cd evolauncher-frontend
npm install
```

### 3. 生成应用图标

图标已自动生成，但如果需要重新生成：

```bash
cd scripts
./create-icons.sh
```

这会从 `dist/Logo.png` 生成：
- `build/icon.icns` (macOS)
- `build/icon.png` (Linux)

---

## 🔧 构建配置说明

### package.json 配置

```json
{
  "build": {
    "appId": "com.evolabeler.app",
    "productName": "EvoLabeler",
    "mac": {
      "target": ["dmg"],
      "arch": ["x64", "arm64"],  // 支持 Intel 和 Apple Silicon
      "icon": "build/icon.icns",
      "category": "public.app-category.developer-tools"
    }
  }
}
```

### 支持的架构

- **x64**: Intel Mac
- **arm64**: Apple Silicon (M1/M2/M3)

构建脚本会自动检测你的 Mac 架构并构建对应版本。

---

## 📦 构建输出

构建完成后，你会在 `release/` 目录找到：

```
release/
├── EvoLabeler-1.0.0.dmg           # DMG 安装包
├── EvoLabeler-1.0.0-mac.zip       # ZIP 压缩包
└── mac/
    └── EvoLabeler.app             # 应用程序
```

---

## 🚀 安装和运行

### 从 DMG 安装

1. 打开 `release/EvoLabeler-*.dmg`
2. 将 EvoLabeler 拖到 Applications 文件夹
3. 从 Applications 启动 EvoLabeler

### 首次运行

macOS 可能会显示安全警告，因为应用未签名：

**解决方法：**

1. 右键点击 EvoLabeler.app
2. 选择"打开"
3. 在弹出对话框中点击"打开"

或者使用命令行：

```bash
xattr -cr /Applications/EvoLabeler.app
```

---

## 🐛 常见问题

### 问题 1: 应用打不开

**症状**: 双击应用无反应或闪退

**解决方案**:

1. 检查控制台日志：
   ```bash
   # 打开控制台.app，查看崩溃报告
   open /Applications/Utilities/Console.app
   ```

2. 移除隔离属性：
   ```bash
   xattr -cr /Applications/EvoLabeler.app
   ```

3. 检查权限：
   ```bash
   chmod -R 755 /Applications/EvoLabeler.app
   ```

### 问题 2: 构建失败

**症状**: electron-builder 报错

**解决方案**:

1. 清理缓存：
   ```bash
   rm -rf node_modules
   rm -rf dist
   rm -rf dist-electron
   rm -rf release
   npm install
   ```

2. 检查 Node.js 版本：
   ```bash
   node --version  # 应该是 18.x 或更高
   ```

3. 重新构建：
   ```bash
   npm run build:mac
   ```

### 问题 3: 图标不显示

**症状**: 应用图标显示为默认图标

**解决方案**:

1. 重新生成图标：
   ```bash
   cd scripts
   ./create-icons.sh
   ```

2. 确认图标文件存在：
   ```bash
   ls -la build/icon.icns
   ```

3. 重新构建应用

### 问题 4: Apple Silicon (M1/M2) 兼容性

**症状**: 在 Apple Silicon Mac 上运行缓慢

**解决方案**:

确保构建时包含 arm64 架构：

```bash
# 检查构建配置
grep -A 5 '"mac":' package.json

# 应该看到: "arch": ["x64", "arm64"]
```

---

## 🔍 调试构建

### 启用详细日志

```bash
DEBUG=electron-builder npm run build:mac
```

### 查看构建产物

```bash
# 查看 asar 包内容
npx asar list release/mac/EvoLabeler.app/Contents/Resources/app.asar

# 提取 asar 包
npx asar extract release/mac/EvoLabeler.app/Contents/Resources/app.asar extracted/
```

---

## 📊 构建性能优化

### 1. 减小应用体积

在 `package.json` 中：

```json
{
  "build": {
    "files": [
      "dist/**/*",
      "dist-electron/**/*",
      "package.json",
      "!**/*.map"  // 排除 source maps
    ],
    "asar": true  // 启用 asar 压缩
  }
}
```

### 2. 加速构建

```bash
# 跳过类型检查（开发时）
npm run build:mac

# 完整检查（发布前）
npm run build:check
```

---

## 🎨 自定义图标

### 替换应用图标

1. 准备一个 1024x1024 的 PNG 图片
2. 替换 `dist/Logo.png`
3. 运行图标生成脚本：
   ```bash
   cd scripts
   ./create-icons.sh
   ```
4. 重新构建应用

### 图标要求

- **格式**: PNG
- **尺寸**: 1024x1024 像素（推荐）
- **背景**: 透明或纯色
- **内容**: 居中，留有边距

---

## 📝 发布清单

在发布应用前，确保：

- [ ] 更新版本号 (`package.json` 中的 `version`)
- [ ] 运行完整构建 (`npm run build:check`)
- [ ] 测试应用在目标 Mac 上运行
- [ ] 检查应用图标显示正常
- [ ] 验证所有功能正常工作
- [ ] 准备发布说明
- [ ] 考虑代码签名（可选）

---

## 🔐 代码签名（可选）

如果你有 Apple Developer 账号，可以签名应用：

1. 获取证书：
   - 登录 Apple Developer
   - 创建 Developer ID Application 证书

2. 更新 `package.json`：
   ```json
   {
     "build": {
       "mac": {
         "identity": "Developer ID Application: Your Name (TEAM_ID)",
         "hardenedRuntime": true,
         "gatekeeperAssess": false
       }
     }
   }
   ```

3. 构建签名版本：
   ```bash
   npm run build:mac
   ```

---

## 📚 相关资源

- [Electron Builder 文档](https://www.electron.build/)
- [Electron 文档](https://www.electronjs.org/docs)
- [macOS 应用分发指南](https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices)

---

## 💡 提示

1. **首次构建**: 第一次构建会下载 Electron 二进制文件，可能需要较长时间
2. **网络问题**: 如果下载缓慢，可以配置镜像（已在 `.npmrc` 中配置）
3. **磁盘空间**: 确保有足够的磁盘空间（至少 2GB）
4. **开发模式**: 使用 `npm run electron:dev` 进行开发和调试

---

## 🆘 获取帮助

如果遇到问题：

1. 查看 [GitHub Issues](https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/issues)
2. 阅读 [Electron Builder 故障排查](https://www.electron.build/troubleshooting)
3. 联系作者: mhumble010221@gmail.com

---

**祝构建顺利！** 🎉


