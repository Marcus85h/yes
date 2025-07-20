// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BEX Token
 * @dev BEX ERC20代币合约
 * 
 * 特性:
 * - 代币名称: BEX
 * - 代币符号: BEX
 * - 精度: 18位小数
 * - 初始总供应量: 130,000,000 BEX (包含18位精度)
 * - 仅合约拥有者可以增发代币
 * - 使用OpenZeppelin的Ownable模块进行权限控制
 */
contract BEXToken is ERC20, Ownable {
    
    /**
     * @dev 构造函数
     * @param initialOwner 初始合约拥有者地址
     * 
     * 初始化代币:
     * - 设置代币名称为"BEX"
     * - 设置代币符号为"BEX"
     * - 初始总供应量为130,000,000个代币(包含18位精度)
     * - 将所有初始代币分配给合约部署者
     */
    constructor(address initialOwner) 
        ERC20("BEX", "BEX") 
        Ownable(initialOwner)
    {
        // 初始总供应量: 130,000,000 BEX
        // 由于ERC20使用18位小数，实际铸造数量为: 130,000,000 * 10^18
        uint256 initialSupply = 130_000_000 * 10**decimals();
        
        // 将所有初始代币分配给合约部署者
        _mint(initialOwner, initialSupply);
    }
    
    /**
     * @dev 增发代币函数
     * @param to 接收代币的地址
     * @param amount 增发数量(不包含小数位)
     * 
     * 要求:
     * - 仅合约拥有者可以调用
     * - 增发数量会自动添加18位小数
     * 
     * 安全特性:
     * - 使用onlyOwner修饰符确保只有拥有者可以调用
     * - 防止向零地址增发代币
     */
    function mint(address to, uint256 amount) 
        external 
        onlyOwner 
    {
        require(to != address(0), "BEX: cannot mint to zero address");
        require(amount > 0, "BEX: amount must be greater than 0");
        
        // 将数量转换为包含18位小数的格式
        uint256 mintAmount = amount * 10**decimals();
        
        // 增发代币
        _mint(to, mintAmount);
    }
    
    /**
     * @dev 获取当前总供应量(不包含小数位)
     * @return 当前总供应量
     */
    function getTotalSupply() external view returns (uint256) {
        return totalSupply() / 10**decimals();
    }
    
    /**
     * @dev 获取指定地址的代币余额(不包含小数位)
     * @param account 查询地址
     * @return 代币余额
     */
    function getBalance(address account) external view returns (uint256) {
        return balanceOf(account) / 10**decimals();
    }
} 