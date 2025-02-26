import streamlit as st
from PIL import Image
import psycopg2
import psycopg2.extras  
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError

# Configuração do banco de dados
DATABASE_URL = "postgresql://postgres:bakerstreet@localhost/animais"
engine = create_engine(DATABASE_URL)
DATABASE_URL2 = "dbname=animais user=postgres password=bakerstreet host=localhost"

# Gerenciamento de sessão do banco de dados (usado para operações de insert, update e delete)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Função para executar consultas SQL usando psycopg2 com RealDictCursor
def executar_query(query, params=None, fetch=False):
    with psycopg2.connect(DATABASE_URL2) as conn:
        # Usando RealDictCursor para que os resultados sejam retornados como dicionários
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            conn.commit()

# Carregar tabelas existentes do banco de dados usando SQLAlchemy
metadata = MetaData()
metadata.reflect(bind=engine)

# Verificar se as tabelas necessárias existem
if "voluntario" not in metadata.tables or "animal" not in metadata.tables:
    st.error("Erro: tabelas 'voluntario' ou 'animal' não foram encontradas no banco de dados.")
else:
    voluntario = metadata.tables["voluntario"]
    animal = metadata.tables["animal"]

    # Interface do Streamlit: exibe a logo centralizada
    img = Image.open("../jupyter/logo.png").resize((200, 200))
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img, caption="Logo")
    
    st.title("Sistema de Gestão de Voluntários e Animais")
    
    # Menu lateral para selecionar a funcionalidade desejada
    menu = st.sidebar.selectbox("Escolha uma opção", ["Gerenciar Voluntários", "Gerenciar Animais"])

    # ------------------------------
    # Gerenciar Voluntários
    # ------------------------------
    if menu == "Gerenciar Voluntários":
        st.subheader("Cadastro de Voluntários")
        
        # Campos para inserir informações do voluntário
        voluntario_id_input = st.number_input("ID do Voluntário (obrigatório)", min_value=1, step=1)
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        contato = st.text_input("Contato")
        areaatuacao = st.text_input("Área de Atuação")

        # Botão para adicionar voluntário
        if st.button("Adicionar Voluntário"):
            if nome and cpf and contato and areaatuacao:
                db_session = SessionLocal()
                try:
                    values = {
                        "id": voluntario_id_input,
                        "nome": nome,
                        "cpf": cpf,
                        "contato": contato,
                        "areaatuacao": areaatuacao
                    }
                    insert_stmt = voluntario.insert().values(**values)
                    db_session.execute(insert_stmt)
                    db_session.commit()
                    st.success("Voluntário cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    db_session.rollback()
                    st.error(f"Erro ao adicionar voluntário: {e}")
                finally:
                    db_session.close()
            else:
                st.error("Todos os campos devem ser preenchidos!")

        # Exibição da lista de voluntários utilizando a função executar_query
        st.subheader("Lista de Voluntários")
        
        # Campo de pesquisa para filtrar por nome ou CPF
        search_voluntario = st.text_input("Pesquisar voluntário (por nome ou CPF):")
        query_voluntarios = "SELECT * FROM voluntario"
        voluntarios = executar_query(query_voluntarios, fetch=True)  # Busca todos os voluntários
        # Filtragem dos resultados, se houver pesquisa
        if search_voluntario:
            search_lower = search_voluntario.lower()
            voluntarios = [v for v in voluntarios if 
                           search_lower in str(v['id']).lower() or 
                           search_lower in v['nome'].lower() or 
                           search_lower in v['cpf'].lower()]

        if not voluntarios:
            st.warning("Nenhum voluntário cadastrado.")
        else:
            for v in voluntarios:
                col1, col2, col3 = st.columns([3, 4, 1])
                with col1:
                    st.write(f"*{v['id']} - {v['nome']}* ({v['cpf']}) - {v['contato']} - {v['areaatuacao']}")
                with col2:
                    with st.expander("Editar"):
                        with st.form(key=f"form_edit_{v['id']}"):
                            novo_nome = st.text_input("Nome", value=v['nome'])
                            novo_cpf = st.text_input("CPF", value=v['cpf'])
                            novo_contato = st.text_input("Contato", value=v['contato'])
                            nova_area = st.text_input("Área de Atuação", value=v['areaatuacao'])
                            submit_edit = st.form_submit_button("Salvar")
                            if submit_edit:
                                db_session = SessionLocal()
                                try:
                                    update_stmt = voluntario.update().where(
                                        voluntario.c.id == v['id']
                                    ).values(
                                        nome=novo_nome,
                                        cpf=novo_cpf,
                                        contato=novo_contato,
                                        areaatuacao=nova_area
                                    )
                                    db_session.execute(update_stmt)
                                    db_session.commit()
                                    st.success("Voluntário atualizado com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    db_session.rollback()
                                    st.error(f"Erro ao atualizar voluntário: {e}")
                                finally:
                                    db_session.close()
                with col3:
                    if st.button("Deletar", key=f"del_voluntario_{v['id']}"):
                        db_session = SessionLocal()
                        try:
                            # Remove registros dependentes antes de deletar o voluntário
                            delete_ep_stmt = text("DELETE FROM eventoparticipantes WHERE idvoluntario = :id")
                            db_session.execute(delete_ep_stmt, {"id": v["id"]})
                            delete_notif_stmt = text("DELETE FROM notificacao WHERE idvoluntario = :id")
                            db_session.execute(delete_notif_stmt, {"id": v["id"]})
                            delete_doacao_stmt = text("DELETE FROM doacao WHERE idvoluntario = :id")
                            db_session.execute(delete_doacao_stmt, {"id": v["id"]})
                            delete_stmt = voluntario.delete().where(voluntario.c.id == v['id'])
                            db_session.execute(delete_stmt)
                            db_session.commit()
                            st.success("Voluntário deletado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            db_session.rollback()
                            st.error(f"Erro ao deletar voluntário: {e}")
                        finally:
                            db_session.close()

    # ------------------------------
    # Gerenciar Animais
    # ------------------------------
    elif menu == "Gerenciar Animais":
        st.subheader("Cadastro de Animais")
        # Campos para inserir informações do animal
        animal_id_input = st.number_input("ID do Animal (obrigatório)", min_value=1, step=1)
        id_lar_temporario = st.number_input("ID Lar Temporário", min_value=0, step=1)
        nome = st.text_input("Nome do animal")
        porte = st.selectbox("Porte", ["Pequeno", "Médio", "Grande"])
        raca = st.text_input("Raça")
        idade = st.number_input("Idade", min_value=0, max_value=50, step=1)
        sexo = st.selectbox("Sexo", ["M", "F"])

        # Botão para adicionar animal
        if st.button("Adicionar animal"):
            if nome and raca:
                db_session = SessionLocal()
                try:
                    values = {
                        "id": animal_id_input,
                        "idlartemporario": id_lar_temporario,
                        "nome": nome,
                        "porte": porte,
                        "raca": raca,
                        "idade": idade,
                        "sexo": sexo
                    }
                    insert_stmt = animal.insert().values(**values)
                    db_session.execute(insert_stmt)
                    db_session.commit()
                    st.success("Animal cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    db_session.rollback()
                    st.error(f"Erro ao adicionar animal: {e}")
                finally:
                    db_session.close()
            else:
                st.error("Nome e raça do animal são obrigatórios!")

        st.subheader("Lista de Animais")
        # Campo de pesquisa para animais
        search_animal = st.text_input("Pesquisar animal (por nome ou ID):")
        query_animais = "SELECT * FROM animal"
        animais = executar_query(query_animais, fetch=True)  # Busca todos os animais
        # Filtra os animais conforme a pesquisa, se fornecida
        if search_animal:
            search_lower = search_animal.lower()
            animais = [a for a in animais if 
                       search_lower in str(a['id']).lower() or 
                       search_lower in a['nome'].lower()]

        if not animais:
            st.warning("Nenhum animal cadastrado.")
        else:
            for a in animais:
                # Organiza a exibição dos dados em três colunas
                col1, col2, col3 = st.columns([3, 4, 1])
                with col1:
                    st.write(f"{a['id']} - {a['nome']} (ID Lar Temporário: {a.get('idlartemporario', 'N/D')}) , {a['porte']}, {a['raca']}, {a['idade']} anos, Sexo: {a['sexo']}")
                with col2:
                    with st.expander("Editar"):
                        with st.form(key=f"form_edit_animal_{a['id']}"):
                            novo_id_lar_temporario = st.number_input(
                                "ID Lar Temporário",
                                value=a['idlartemporario'] if a['idlartemporario'] is not None else 0,
                                step=1
                            )
                            novo_nome = st.text_input("Nome", value=a['nome'])
                            novo_porte = st.selectbox("Porte", ["Pequeno", "Médio", "Grande"],
                                                      index=["Pequeno", "Médio", "Grande"].index(a['porte']))
                            novo_raca = st.text_input("Raça", value=a['raca'])
                            nova_idade = st.number_input("Idade", min_value=0, max_value=50, step=1, value=a['idade'])
                            novo_sexo = st.selectbox("Sexo", ["M", "F"],
                                                     index=["M", "F"].index(a['sexo']))
                            submit_edit_animal = st.form_submit_button("Salvar")
                            if submit_edit_animal:
                                db_session = SessionLocal()
                                try:
                                    update_stmt = animal.update().where(
                                        animal.c.id == a['id']
                                    ).values(
                                        idlartemporario=novo_id_lar_temporario,
                                        nome=novo_nome,
                                        porte=novo_porte,
                                        raca=novo_raca,
                                        idade=nova_idade,
                                        sexo=novo_sexo
                                    )
                                    db_session.execute(update_stmt)
                                    db_session.commit()
                                    st.success("Animal atualizado com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    db_session.rollback()
                                    st.error(f"Erro ao atualizar animal: {e}")
                                finally:
                                    db_session.close()
                with col3:
                    if st.button("Deletar", key=f"del_animal_{a['id']}"):
                        db_session = SessionLocal()
                        try:
                            # Remove as referências do animal em outras tabelas antes de excluí-lo
                            delete_rs_stmt = text("DELETE FROM registrosaude WHERE idanimal = :id")
                            db_session.execute(delete_rs_stmt, {"id": a["id"]})
                            
                            delete_tc_stmt = text("DELETE FROM testeconvivio WHERE idanimal = :id")
                            db_session.execute(delete_tc_stmt, {"id": a["id"]})
                            
                            delete_feedback_stmt = text(
                                "DELETE FROM feedback WHERE idadocao IN (SELECT id FROM adocao WHERE idanimal = :id)"
                            )
                            db_session.execute(delete_feedback_stmt, {"id": a["id"]})
                            
                            delete_adocao_stmt = text("DELETE FROM adocao WHERE idanimal = :id")
                            db_session.execute(delete_adocao_stmt, {"id": a["id"]})
                            
                            delete_stmt = animal.delete().where(animal.c.id == a['id'])
                            db_session.execute(delete_stmt)
                            db_session.commit()
                            st.success("Animal deletado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            db_session.rollback()
                            st.error(f"Erro ao deletar animal: {e}")
                        finally:
                            db_session.close()
