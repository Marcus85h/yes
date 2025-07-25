import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../config/app_config.dart';
import 'api_service.dart';

/// 支付方式枚举
enum PaymentMethod {
  alipay,
  wechat,
  applePay,
  googlePay,
}

/// 支付状态枚举
enum PaymentStatus {
  pending,
  success,
  failed,
  cancelled,
}

/// 支付订单信息
class PaymentOrder {
  final String orderId;
  final String productId;
  final String productName;
  final double amount;
  final PaymentMethod method;
  final String? description;
  final Map<String, dynamic>? metadata;
  
  PaymentOrder({
    required this.orderId,
    required this.productId,
    required this.productName,
    required this.amount,
    required this.method,
    this.description,
    this.metadata,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'order_id': orderId,
      'product_id': productId,
      'product_name': productName,
      'amount': amount,
      'method': method.name,
      'description': description,
      'metadata': metadata,
    };
  }
}

/// 支付结果
class PaymentResult {
  final bool success;
  final String? transactionId;
  final String? errorMessage;
  final PaymentStatus status;
  final Map<String, dynamic>? data;
  
  PaymentResult({
    required this.success,
    this.transactionId,
    this.errorMessage,
    required this.status,
    this.data,
  });
  
  factory PaymentResult.success(String transactionId, {Map<String, dynamic>? data}) {
    return PaymentResult(
      success: true,
      transactionId: transactionId,
      status: PaymentStatus.success,
      data: data,
    );
  }
  
  factory PaymentResult.failed(String errorMessage, {PaymentStatus status = PaymentStatus.failed}) {
    return PaymentResult(
      success: false,
      errorMessage: errorMessage,
      status: status,
    );
  }
}

class PaymentService {
  static PaymentService? _instance;
  static PaymentService get instance => _instance ??= PaymentService._();
  
  PaymentService._();
  
  /// 创建支付订单
  Future<PaymentOrder?> createOrder({
    required String productId,
    required String productName,
    required double amount,
    required PaymentMethod method,
    String? description,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await ApiService.createPaymentOrder({
        'product_id': productId,
        'product_name': productName,
        'amount': amount,
        'payment_method': method.name,
        'description': description,
        'metadata': metadata,
      });
      
      return PaymentOrder(
        orderId: response['order_id'],
        productId: productId,
        productName: productName,
        amount: amount,
        method: method,
        description: description,
        metadata: metadata,
      );
      
    } catch (e) {
      print('创建支付订单失败: $e');
      return null;
    }
  }
  
  /// 发起支付
  Future<PaymentResult> pay(PaymentOrder order) async {
    try {
      switch (order.method) {
        case PaymentMethod.alipay:
          return await _payWithAlipay(order);
        case PaymentMethod.wechat:
          return await _payWithWechat(order);
        case PaymentMethod.applePay:
          return await _payWithApplePay(order);
        case PaymentMethod.googlePay:
          return await _payWithGooglePay(order);
      }
    } catch (e) {
      return PaymentResult.failed('支付失败: $e');
    }
  }
  
  /// 支付宝支付
  Future<PaymentResult> _payWithAlipay(PaymentOrder order) async {
    try {
      // 获取支付宝支付参数
      final response = await ApiService.getAlipayParams(order.orderId);
      final payParams = response['pay_params'];
      
      // 调用支付宝SDK
      // 这里需要集成支付宝Flutter插件
      // final result = await Alipay.pay(payParams);
      
      // 模拟支付结果
      await Future.delayed(const Duration(seconds: 2));
      final result = {'resultStatus': '9000', 'result': 'success'};
      
      if (result['resultStatus'] == '9000') {
        // 验证支付结果
        final verified = await _verifyPayment(order.orderId);
        if (verified) {
          return PaymentResult.success(
            result['result'] ?? '',
            data: result,
          );
        } else {
          return PaymentResult.failed('支付验证失败');
        }
      } else {
        return PaymentResult.failed('支付失败: ${result['resultStatus']}');
      }
      
    } catch (e) {
      return PaymentResult.failed('支付宝支付失败: $e');
    }
  }
  
  /// 微信支付
  Future<PaymentResult> _payWithWechat(PaymentOrder order) async {
    try {
      // 获取微信支付参数
      final response = await ApiService.getWechatPayParams(order.orderId);
      final payParams = response['pay_params'];
      
      // 调用微信支付SDK
      // 这里需要集成微信支付Flutter插件
      // final result = await WechatPay.pay(payParams);
      
      // 模拟支付结果
      await Future.delayed(const Duration(seconds: 2));
      final result = {'errCode': 0, 'errStr': 'success'};
      
      if (result['errCode'] == 0) {
        // 验证支付结果
        final verified = await _verifyPayment(order.orderId);
        if (verified) {
          return PaymentResult.success(
            result['errStr'] ?? '',
            data: result,
          );
        } else {
          return PaymentResult.failed('支付验证失败');
        }
      } else {
        return PaymentResult.failed('微信支付失败: ${result['errStr']}');
      }
      
    } catch (e) {
      return PaymentResult.failed('微信支付失败: $e');
    }
  }
  
  /// Apple Pay支付
  Future<PaymentResult> _payWithApplePay(PaymentOrder order) async {
    try {
      // 检查Apple Pay是否可用
      // final isAvailable = await ApplePay.isAvailable();
      // if (!isAvailable) {
      //   return PaymentResult.failed('Apple Pay不可用');
      // }
      
      // 创建Apple Pay支付请求
      // final paymentRequest = await ApplePay.createPaymentRequest({
      //   'merchantIdentifier': AppConfig.applePayMerchantId,
      //   'supportedNetworks': ['visa', 'mastercard'],
      //   'merchantCapabilities': ['3ds', 'emv'],
      //   'countryCode': 'CN',
      //   'currencyCode': 'CNY',
      //   'total': {
      //     'label': order.productName,
      //     'amount': order.amount.toString(),
      //   },
      // });
      
      // 发起Apple Pay支付
      // final result = await ApplePay.pay(paymentRequest);
      
      // 模拟支付结果
      await Future.delayed(const Duration(seconds: 2));
      final result = {'status': 'success', 'transactionId': 'apple_${DateTime.now().millisecondsSinceEpoch}'};
      
      if (result['status'] == 'success') {
        // 验证支付结果
        final verified = await _verifyPayment(order.orderId);
        if (verified) {
          return PaymentResult.success(
            result['transactionId'],
            data: result,
          );
        } else {
          return PaymentResult.failed('支付验证失败');
        }
      } else {
        return PaymentResult.failed('Apple Pay支付失败');
      }
      
    } catch (e) {
      return PaymentResult.failed('Apple Pay支付失败: $e');
    }
  }
  
  /// Google Pay支付
  Future<PaymentResult> _payWithGooglePay(PaymentOrder order) async {
    try {
      // 检查Google Pay是否可用
      // final isAvailable = await GooglePay.isAvailable();
      // if (!isAvailable) {
      //   return PaymentResult.failed('Google Pay不可用');
      // }
      
      // 创建Google Pay支付请求
      // final paymentRequest = {
      //   'apiVersion': 2,
      //   'apiVersionMinor': 0,
      //   'allowedPaymentMethods': [{
      //     'type': 'CARD',
      //     'parameters': {
      //       'allowedAuthMethods': ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
      //       'allowedCardNetworks': ['VISA', 'MASTERCARD'],
      //     },
      //     'tokenizationSpecification': {
      //       'type': 'PAYMENT_GATEWAY',
      //       'parameters': {
      //         'gateway': 'example',
      //         'gatewayMerchantId': 'exampleGatewayMerchantId',
      //       },
      //     },
      //   }],
      //   'merchantInfo': {
      //     'merchantName': 'Example Merchant',
      //   },
      //   'transactionInfo': {
      //     'totalPriceStatus': 'FINAL',
      //     'totalPrice': order.amount.toString(),
      //     'currencyCode': 'CNY',
      //     'countryCode': 'CN',
      //   },
      // };
      
      // 发起Google Pay支付
      // final result = await GooglePay.pay(paymentRequest);
      
      // 模拟支付结果
      await Future.delayed(const Duration(seconds: 2));
      final result = {'status': 'success', 'transactionId': 'google_${DateTime.now().millisecondsSinceEpoch}'};
      
      if (result['status'] == 'success') {
        // 验证支付结果
        final verified = await _verifyPayment(order.orderId);
        if (verified) {
          return PaymentResult.success(
            result['transactionId'],
            data: result,
          );
        } else {
          return PaymentResult.failed('支付验证失败');
        }
      } else {
        return PaymentResult.failed('Google Pay支付失败');
      }
      
    } catch (e) {
      return PaymentResult.failed('Google Pay支付失败: $e');
    }
  }
  
  /// 验证支付结果
  Future<bool> _verifyPayment(String orderId) async {
    try {
      final response = await ApiService.verifyPayment(orderId);
      return response['verified'] == true;
    } catch (e) {
      print('验证支付失败: $e');
      return false;
    }
  }
  
  /// 查询支付状态
  Future<PaymentStatus> queryPaymentStatus(String orderId) async {
    try {
      final response = await ApiService.queryPaymentStatus(orderId);
      final status = response['status'];
      
      switch (status) {
        case 'pending':
          return PaymentStatus.pending;
        case 'success':
          return PaymentStatus.success;
        case 'failed':
          return PaymentStatus.failed;
        case 'cancelled':
          return PaymentStatus.cancelled;
        default:
          return PaymentStatus.pending;
      }
    } catch (e) {
      print('查询支付状态失败: $e');
      return PaymentStatus.failed;
    }
  }
  
  /// 获取支付历史
  Future<List<Map<String, dynamic>>> getPaymentHistory({int page = 1, int pageSize = 20}) async {
    try {
      final response = await ApiService.getPaymentHistory(page: page, pageSize: pageSize);
      return List<Map<String, dynamic>>.from(response['results'] ?? []);
    } catch (e) {
      print('获取支付历史失败: $e');
      return [];
    }
  }
  
  /// 申请退款
  Future<bool> requestRefund(String orderId, {String? reason}) async {
    try {
      final response = await ApiService.requestRefund(orderId, reason: reason);
      return response['success'] == true;
    } catch (e) {
      print('申请退款失败: $e');
      return false;
    }
  }
}

/// 支付配置
class PaymentConfig {
  static const String alipayAppId = 'your_alipay_app_id';
  static const String wechatAppId = 'your_wechat_app_id';
  static const String applePayMerchantId = 'your_apple_pay_merchant_id';
  static const String googlePayMerchantId = 'your_google_pay_merchant_id';
  
  static const List<PaymentMethod> supportedMethods = [
    PaymentMethod.alipay,
    PaymentMethod.wechat,
    PaymentMethod.applePay,
    PaymentMethod.googlePay,
  ];
} 