from model_sample import db, PaymentWay

# ---- 支払い方法データの挿入 ----
def add_payment_methods():
    dummy_payment_methods = [
        PaymentWay(paymentWayName='現金'),
        PaymentWay(paymentWayName='クレジットカード'),
        PaymentWay(paymentWayName='コンビニ'),
        PaymentWay(paymentWayName='PayPay')
    ]
    db.session.add_all(dummy_payment_methods)
    db.session.commit()