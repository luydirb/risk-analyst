import pandas as pd
from datetime import datetime, timedelta

# Carregar os dados
data = pd.read_csv('transactional-sample.csv')
data['transaction_date'] = pd.to_datetime(data['transaction_date'])

# Calcular a média do valor das transações
transaction_mean = data['transaction_amount'].mean()

# Identificar dispositivos suspeitos
device_user_counts = data.groupby('device_id')['user_id'].nunique().reset_index()
suspect_devices = device_user_counts[device_user_counts['user_id'] > 1]['device_id'].tolist()

# Adicionar diferença de tempo entre transações
data = data.sort_values(by=['user_id', 'transaction_date'])
data['time_diff'] = data.groupby('user_id')['transaction_date'].diff().dt.total_seconds().fillna(0)

# Lista para armazenar os resultados das transações
results = []

# Função anti-fraude simples atualizada para retornar o número da transação e se foi aprovada ou negada
def simple_anti_fraud(transaction, transaction_id):
    # Verificar valor da transação
    if transaction['transaction_amount'] > 3 * transaction_mean:
        return transaction_id, "Negar"

    # Verificar dispositivo suspeito
    if transaction['device_id'] in suspect_devices:
        return transaction_id, "Negar"

    # Verificar transações frequentes
    user_transactions = data[data['user_id'] == transaction['user_id']]
    if not user_transactions.empty:
        last_transaction = user_transactions.iloc[-1]
        time_diff = (transaction['transaction_date'] - last_transaction['transaction_date']).total_seconds()
        if time_diff < 300:  # Menos de 5 minutos
            return transaction_id, "Negar"

    return transaction_id, "Aprovar"

# Aplicar a função a todas as transações e armazenar os resultados
for index, row in data.iterrows():
    transaction = row.to_dict()
    transaction_id, result = simple_anti_fraud(transaction, transaction['transaction_id'])
    results.append((transaction_id, result))

# Criar um DataFrame com os resultados
results_df = pd.DataFrame(results, columns=['transaction_id', 'result'])

# Salvar os resultados em um arquivo Excel
output_file_path = 'transaction_results.xlsx'
results_df.to_excel(output_file_path, index=False)
