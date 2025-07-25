import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/services/payment_service.dart';
import '../../../core/theme/app_theme.dart';

class PaymentPage extends StatefulWidget {
  final String productId;
  final String productName;
  final double amount;
  final String? description;

  const PaymentPage({
    Key? key,
    required this.productId,
    required this.productName,
    required this.amount,
    this.description,
  }) : super(key: key);

  @override
  State<PaymentPage> createState() => _PaymentPageState();
}

class _PaymentPageState extends State<PaymentPage> {
  final PaymentService _paymentService = PaymentService.instance;
  
  PaymentMethod _selectedMethod = PaymentMethod.alipay;
  bool _isLoading = false;
  String? _errorMessage;
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('支付'),
        backgroundColor: theme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // 商品信息
          _buildProductInfo(),
          
          // 支付方式选择
          _buildPaymentMethods(),
          
          // 支付按钮
          _buildPaymentButton(),
          
          // 错误信息
          if (_errorMessage != null)
            _buildErrorMessage(),
        ],
      ),
    );
  }
  
  /// 构建商品信息
  Widget _buildProductInfo() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '商品信息',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: Colors.blue[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.shopping_cart,
                  color: Colors.blue[600],
                  size: 30,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.productName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (widget.description != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        widget.description!,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Text(
                '¥${widget.amount.toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  /// 构建支付方式选择
  Widget _buildPaymentMethods() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Text(
              '选择支付方式',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
          ),
          ...PaymentConfig.supportedMethods.map((method) => _buildPaymentMethodTile(method)),
        ],
      ),
    );
  }
  
  /// 构建支付方式选项
  Widget _buildPaymentMethodTile(PaymentMethod method) {
    final isSelected = _selectedMethod == method;
    
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedMethod = method;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue[50] : Colors.transparent,
          border: Border(
            bottom: BorderSide(
              color: Colors.grey[200]!,
              width: 0.5,
            ),
          ),
        ),
        child: Row(
          children: [
            // 支付方式图标
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: _getPaymentMethodColor(method),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                _getPaymentMethodIcon(method),
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            // 支付方式名称
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _getPaymentMethodName(method),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Text(
                    _getPaymentMethodDescription(method),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            // 选择指示器
            if (isSelected)
              Icon(
                Icons.check_circle,
                color: Colors.blue[600],
                size: 24,
              )
            else
              Icon(
                Icons.radio_button_unchecked,
                color: Colors.grey[400],
                size: 24,
              ),
          ],
        ),
      ),
    );
  }
  
  /// 构建支付按钮
  Widget _buildPaymentButton() {
    return Container(
      margin: const EdgeInsets.all(16),
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _processPayment,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.orange[600],
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 2,
        ),
        child: _isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2,
                ),
              )
            : Text(
                '立即支付 ¥${widget.amount.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
      ),
    );
  }
  
  /// 构建错误信息
  Widget _buildErrorMessage() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Row(
        children: [
          Icon(
            Icons.error_outline,
            color: Colors.red[600],
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _errorMessage!,
              style: TextStyle(
                color: Colors.red[600],
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  /// 处理支付
  Future<void> _processPayment() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      // 创建支付订单
      final order = await _paymentService.createOrder(
        productId: widget.productId,
        productName: widget.productName,
        amount: widget.amount,
        method: _selectedMethod,
        description: widget.description,
      );
      
      if (order == null) {
        throw Exception('创建支付订单失败');
      }
      
      // 发起支付
      final result = await _paymentService.pay(order);
      
      if (result.success) {
        // 支付成功
        _showSuccessDialog(result);
      } else {
        // 支付失败
        setState(() {
          _errorMessage = result.errorMessage ?? '支付失败';
        });
      }
      
    } catch (e) {
      setState(() {
        _errorMessage = '支付异常: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  /// 显示支付成功对话框
  void _showSuccessDialog(PaymentResult result) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.check_circle,
              color: Colors.green[600],
              size: 28,
            ),
            const SizedBox(width: 8),
            const Text('支付成功'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('商品: ${widget.productName}'),
            Text('金额: ¥${widget.amount.toStringAsFixed(2)}'),
            Text('支付方式: ${_getPaymentMethodName(_selectedMethod)}'),
            if (result.transactionId != null)
              Text('交易号: ${result.transactionId}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(true); // 返回支付成功
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
  
  /// 获取支付方式颜色
  Color _getPaymentMethodColor(PaymentMethod method) {
    switch (method) {
      case PaymentMethod.alipay:
        return Colors.blue[600]!;
      case PaymentMethod.wechat:
        return Colors.green[600]!;
      case PaymentMethod.applePay:
        return Colors.black;
      case PaymentMethod.googlePay:
        return Colors.blue[800]!;
    }
  }
  
  /// 获取支付方式图标
  IconData _getPaymentMethodIcon(PaymentMethod method) {
    switch (method) {
      case PaymentMethod.alipay:
        return Icons.account_balance_wallet;
      case PaymentMethod.wechat:
        return Icons.chat;
      case PaymentMethod.applePay:
        return Icons.apple;
      case PaymentMethod.googlePay:
        return Icons.android;
    }
  }
  
  /// 获取支付方式名称
  String _getPaymentMethodName(PaymentMethod method) {
    switch (method) {
      case PaymentMethod.alipay:
        return '支付宝';
      case PaymentMethod.wechat:
        return '微信支付';
      case PaymentMethod.applePay:
        return 'Apple Pay';
      case PaymentMethod.googlePay:
        return 'Google Pay';
    }
  }
  
  /// 获取支付方式描述
  String _getPaymentMethodDescription(PaymentMethod method) {
    switch (method) {
      case PaymentMethod.alipay:
        return '推荐使用支付宝支付';
      case PaymentMethod.wechat:
        return '推荐使用微信支付';
      case PaymentMethod.applePay:
        return 'Apple设备专用';
      case PaymentMethod.googlePay:
        return 'Android设备专用';
    }
  }
} 