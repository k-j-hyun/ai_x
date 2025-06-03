from flask import Blueprint, render_template, request
from model.forecast import predict_demand
from app.db import get_product_data
from db import get_product_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        input_date = request.form.get('date')
        
        # 예측 수행
        prediction = predict_demand(product_id, input_date)
        
        return render_template('result.html', prediction=prediction, product_id=product_id, date=input_date)
    
    # GET 요청: 제품 목록 불러오기 (Oracle에서)
    product_list = get_product_data()
    return render_template('predict.html', products=product_list)