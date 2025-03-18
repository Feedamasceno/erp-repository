import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px  # Importar plotly para gráficos interativos

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios", "Status Contas"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        # Exibir tabela de contas a pagar
        df_contas = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df_contas)
        
        # Consultar a distribuição por fornecedor
        query = '''
        SELECT fornecedor, SUM(valor) AS total_devido
        FROM contas_pagar
        GROUP BY fornecedor
        ORDER BY total_devido DESC
        '''
        df_fornecedores = pd.read_sql_query(query, conn)
        
        # Mostrar o gráfico de pizza para a distribuição das contas a pagar
        if not df_fornecedores.empty:
            fig1 = px.pie(df_fornecedores, names='fornecedor', values='total_devido', title='Distribuição das Contas a Pagar por Fornecedor')
            st.plotly_chart(fig1)
        else:
            st.write("Nenhuma conta a pagar registrada.")
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Top 5 Clientes com Maior Receita")
        
        # Consulta SQL corrigida com JOIN
        query_top5 = '''
        SELECT c.nome AS cliente, SUM(cr.valor) AS total_receita
        FROM contas_receber cr
        JOIN clientes c ON cr.cliente_id = c.id
        GROUP BY c.nome
        ORDER BY total_receita DESC
        LIMIT 5
        '''
        df_top5 = pd.read_sql_query(query_top5, conn)
        
        if not df_top5.empty:
            # Exibir tabela com o Top 5 Clientes
            st.table(df_top5)
            
            # Exibir gráfico de barras para o Top 5 Clientes
            fig = px.bar(df_top5, x='cliente', y='total_receita', title="Top 5 Clientes com Maior Receita",
                         labels={'cliente': 'Cliente', 'total_receita': 'Receita Total (R$)'},
                         text_auto=True)
            st.plotly_chart(fig)
        else:
            st.write("Nenhuma receita registrada para clientes.")
    
    elif choice == "Status Contas":
        st.subheader("Status das Contas a Pagar e Receber")
        
        # Contas a Pagar: Status (Pendente ou Pago)
        query_status_pagar = '''
        SELECT status, COUNT(*) as quantidade, SUM(valor) as total
        FROM contas_pagar
        GROUP BY status
        '''
        df_status_pagar = pd.read_sql_query(query_status_pagar, conn)
        
        # Contas a Receber: Status (Pendente ou Recebido)
        query_status_receber = '''
        SELECT status, COUNT(*) as quantidade, SUM(valor) as total
        FROM contas_receber
        GROUP BY status
        '''
        df_status_receber = pd.read_sql_query(query_status_receber, conn)
        
        # Exibir gráficos lado a lado
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Contas a Pagar")
            if not df_status_pagar.empty:
                fig3 = px.bar(df_status_pagar, x='status', y='total', title="Status das Contas a Pagar", text_auto=True)
                st.plotly_chart(fig3)
            else:
                st.write("Nenhuma conta a pagar registrada.")
        
        with col2:
            st.subheader("Contas a Receber")
            if not df_status_receber.empty:
                fig4 = px.bar(df_status_receber, x='status', y='total', title="Status das Contas a Receber", text_auto=True)
                st.plotly_chart(fig4)
            else:
                st.write("Nenhuma conta a receber registrada.")
    
    conn.close()

if __name__ == "__main__":
    main()
