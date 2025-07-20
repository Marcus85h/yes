# BEX Token - ERC20代币合约

这是一个基于Solidity和OpenZeppelin库开发的BEX ERC20代币智能合约。

## 合约特性

- **代币名称**: BEX
- **代币符号**: BEX
- **精度**: 18位小数
- **初始总供应量**: 130,000,000 BEX (包含18位精度)
- **权限控制**: 使用OpenZeppelin的Ownable模块
- **增发功能**: 仅合约拥有者可以增发代币

## 技术规格

- **Solidity版本**: 0.8.20
- **OpenZeppelin版本**: 5.0.0
- **网络兼容性**: 以太坊主网、测试网及兼容EVM的区块链

## 安装和设置

1. 安装依赖：
```bash
npm install
```

2. 编译合约：
```bash
npx hardhat compile
```

3. 运行测试：
```bash
npx hardhat test
```

4. 部署合约：
```bash
npx hardhat run scripts/deploy.js --network <network-name>
```

## 合约功能

### 构造函数
```solidity
constructor(address initialOwner)
```
- 设置代币名称为"BEX"
- 设置代币符号为"BEX"
- 初始总供应量为130,000,000个代币
- 将所有初始代币分配给合约部署者
- 设置合约拥有者

### mint函数
```solidity
function mint(address to, uint256 amount) external onlyOwner
```
- 仅合约拥有者可以调用
- 向指定地址增发指定数量的代币
- 自动处理18位小数精度
- 包含安全检查（防止向零地址增发、数量必须大于0）

### 辅助函数
```solidity
function getTotalSupply() external view returns (uint256)
function getBalance(address account) external view returns (uint256)
```
- 提供便捷的查询功能
- 返回不包含小数位的数值

## 安全特性

1. **权限控制**: 使用OpenZeppelin的Ownable模块确保只有拥有者可以增发代币
2. **输入验证**: 防止向零地址增发代币，确保增发数量大于0
3. **标准ERC20**: 完全兼容ERC20标准，支持所有标准功能
4. **溢出保护**: 使用Solidity 0.8.x的内置溢出检查
5. **重入攻击防护**: 使用OpenZeppelin的安全实现

## 使用示例

### 部署合约
```javascript
const BEXToken = await ethers.getContractFactory("BEXToken");
const bexToken = await BEXToken.deploy(deployerAddress);
```

### 增发代币
```javascript
// 只有合约拥有者可以调用
await bexToken.mint(recipientAddress, 1000); // 增发1000个BEX
```

### 查询余额
```javascript
const balance = await bexToken.getBalance(userAddress);
console.log(`用户余额: ${balance} BEX`);
```

### 转账
```javascript
await bexToken.transfer(recipientAddress, ethers.parseUnits("100", 18));
```

## 测试

运行完整的测试套件：
```bash
npx hardhat test
```

测试覆盖：
- 合约部署和初始化
- 代币增发功能
- 权限控制
- ERC20标准功能
- 边界条件和安全检查

## 许可证

MIT License

## 注意事项

1. 部署前请确保了解合约的所有功能和风险
2. 在生产环境部署前，建议进行全面的安全审计
3. 合约拥有者拥有增发代币的权限，请妥善保管私钥
4. 建议在测试网络上充分测试后再部署到主网 