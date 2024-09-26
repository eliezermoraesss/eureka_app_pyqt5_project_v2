from datetime import datetime

import pyodbc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.open_search_dialog import open_search_dialog
from src.app.utils.save_log_database import save_log_database
from src.app.utils.search_queries import select_query
from src.qt.ui.ui_new_product_window import Ui_NewProductWindow


def execute_validate_query(entity, field):
    query = select_query(entity)
    query = query[1].replace(":search_field", f"{field}")  # Índice [1] filtra pelo código da entidade

    driver = '{SQL Server}'
    username, password, database, server = setup_mssql()
    try:
        with pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}') as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result if result is not None else None

    except Exception as ex:
        QMessageBox.warning(None, f"Eureka® - Falha ao conectar no banco de dados",
                            f"Erro ao consultar {field}.\n\n{str(ex)}\n\nContate o administrador do sistema.")


class NewProductWindow(QtWidgets.QDialog):
    def __init__(self):
        super(NewProductWindow, self).__init__()

        self.existe_cadastro = False
        self.driver = '{SQL Server}'
        self.username, self.password, self.database, self.server = setup_mssql()

        self.required_field_is_blank = False
        self.selected_row = []
        self.user_data = load_session()
        self.setFixedSize(640, 600)
        self.ui = Ui_NewProductWindow()
        self.ui.setupUi(self)
        self.entity_names = {
            "descricao": "DESCRIÇÃO",
            "tipo": "TIPO",
            "unidade_medida": "UNID. MEDIDA",
            "armazem": "ARMAZÉM",
            "centro_custo": "CENTRO DE CUSTO",
            "grupo": "GRUPO"
        }
        self.required_fields = {
            "codigo": self.ui.codigo_field,
            "descricao": self.ui.descricao_field,
            "tipo": self.ui.tipo_field,
            "unidade_medida": self.ui.um_field,
            "armazem": self.ui.armazem_field,
            "centro_custo": self.ui.cc_field,
            "grupo": self.ui.grupo_field
        }
        self.init_ui()

    def init_ui(self):
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.insert_product)
        self.ui.btn_search_tipo.clicked.connect(lambda: open_search_dialog("Tipo", self.ui.tipo_field, "tipo"))
        self.ui.btn_search_um.clicked.connect(
            lambda: open_search_dialog("Unidade de Medida", self.ui.um_field, "unidade_medida"))
        self.ui.btn_search_arm.clicked.connect(lambda: open_search_dialog("Armazém", self.ui.armazem_field, "armazem"))
        self.ui.btn_search_cc.clicked.connect(
            lambda: open_search_dialog("Centro de Custo", self.ui.cc_field, "centro_custo"))
        self.ui.btn_search_grupo.clicked.connect(lambda: open_search_dialog("Grupo", self.ui.grupo_field, "grupo"))

        self.ui.tipo_field.textChanged.connect(
            lambda: self.validate_required_fields("tipo", self.ui.tipo_field.text().upper()))
        self.ui.um_field.textChanged.connect(
            lambda: self.validate_required_fields("unidade_medida", self.ui.um_field.text().upper()))
        self.ui.armazem_field.textChanged.connect(
            lambda: self.validate_required_fields("armazem", self.ui.armazem_field.text().upper()))
        self.ui.cc_field.textChanged.connect(
            lambda: self.validate_required_fields("centro_custo", self.ui.cc_field.text().upper()))
        self.ui.grupo_field.textChanged.connect(self.on_grupo_field_changed)
        self.ui.grupo_field.textChanged.connect(
            lambda: self.validate_required_fields("grupo", self.ui.grupo_field.text().upper()))

        self.ui.codigo_field.returnPressed.connect(self.insert_product)
        self.ui.descricao_field.returnPressed.connect(self.insert_product)
        self.ui.desc_comp_field.returnPressed.connect(self.insert_product)
        self.ui.tipo_field.returnPressed.connect(self.insert_product)
        self.ui.um_field.returnPressed.connect(self.insert_product)
        self.ui.armazem_field.returnPressed.connect(self.insert_product)
        self.ui.cc_field.returnPressed.connect(self.insert_product)
        self.ui.grupo_field.returnPressed.connect(self.insert_product)
        self.ui.endereco_field.returnPressed.connect(self.insert_product)

    def validate_required_fields(self, entity, field):
        if field != '':
            validated = execute_validate_query(entity, field)
            if validated is None:
                required_field = self.required_fields[entity]
                required_field.clear()
                QMessageBox.information(self, "Eureka®",
                                        f"Nenhum resultado encontrado para o campo {self.entity_names[entity]} com o "
                                        f"valor {field}")
        elif entity == 'grupo':
            self.ui.desc_grupo_field.setText("")

    def on_grupo_field_changed(self, field_value):
        if field_value:
            self.fetch_group_description(field_value)

    def verify_blank_required_fields(self):
        self.required_field_is_blank = False
        for field_name, field_object in self.required_fields.items():
            if field_name != 'centro_custo' and not field_object.text():
                QMessageBox.information(self, 'Eureka®', f"O campo {self.entity_names[field_name]} é obrigatório e não "
                                                         f"pode estar vazio.")
                self.required_field_is_blank = True

    def verificar_se_existe_cadastro(self, codigo):
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}') as conn:
                query = f"SELECT B1_COD FROM PROTHEUS12_R27.dbo.SB1010 WHERE B1_COD LIKE '{codigo}%' AND D_E_L_E_T_ <> '*';"
                cursor = conn.cursor()
                result = cursor.execute(query).fetchone()

                if result is not None:
                    QMessageBox.warning(None, f"Eureka® {codigo}", f"Já existe cadastro deste produto.\nVerifique e tente novamente!")
                    return True
                else:
                    return False

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Erro ao consultar banco de dados TOTVS",
                                f"Não foi possível obter última chave primária da tabela de produtos SB1010.\n\n{str(ex)}"
                                f"\n\nContate o administrador do sistema.")
            return None

    def insert_query(self):
        codigo = self.ui.codigo_field.text().upper()
        descricao = self.ui.descricao_field.text().upper()
        descricao_compl = self.ui.desc_comp_field.text().upper()
        tipo = self.ui.tipo_field.text().upper()
        unidade = self.ui.um_field.text().upper()
        armazem = self.ui.armazem_field.text().upper()
        grupo = self.ui.grupo_field.text().upper()
        descricao_grupo = self.ui.desc_grupo_field.text().upper()
        centro_custo = self.ui.cc_field.text().upper()
        bloquear = self.ui.bloquear_combobox.currentText()
        endereco = self.ui.endereco_field.text().upper()

        data_cadastro = datetime.now().strftime("%Y%m%d")
        chave_primaria = self.nova_chave_primaria()

        if chave_primaria is None:
            return

        query = f"""
                INSERT INTO 
                    PROTHEUS12_R27.dbo.SB1010 
                    (B1_AFAMAD, B1_FILIAL, B1_COD, B1_DESC, B1_XDESC2, B1_CODITE, B1_TIPO, B1_UM, B1_LOCPAD, B1_GRUPO, 
                    B1_ZZLOCAL, B1_POSIPI, B1_ESPECIE, B1_EX_NCM, B1_EX_NBM, B1_PICM, B1_IPI, B1_ALIQISS, B1_CODISS, 
                    B1_TE, B1_TS, B1_PICMRET, B1_BITMAP, B1_SEGUM, B1_PICMENT, B1_IMPZFRC, B1_CONV, B1_TIPCONV, 
                    B1_ALTER, B1_QE, B1_PRV1, B1_EMIN, B1_CUSTD, B1_UCALSTD, B1_UCOM, B1_UPRC, B1_MCUSTD, B1_ESTFOR, 
                    B1_PESO, B1_ESTSEG, B1_FORPRZ, B1_PE, B1_TIPE, B1_LE, B1_LM, B1_CONTA, B1_TOLER, B1_CC, B1_ITEMCC, 
                    B1_PROC, B1_LOJPROC, B1_FAMILIA, B1_QB, B1_APROPRI, B1_TIPODEC, B1_ORIGEM, B1_CLASFIS, B1_UREV, 
                    B1_DATREF, B1_FANTASM, B1_RASTRO, B1_FORAEST, B1_COMIS, B1_DTREFP1, B1_MONO, B1_PERINV, B1_GRTRIB, 
                    B1_MRP, B1_NOTAMIN, B1_CONINI, B1_CONTSOC, B1_PRVALID, B1_CODBAR, B1_GRADE, B1_NUMCOP, B1_FORMLOT, 
                    B1_IRRF, B1_FPCOD, B1_CODGTIN, B1_DESC_P, B1_CONTRAT, B1_DESC_GI, B1_DESC_I, B1_LOCALIZ, B1_OPERPAD,
                    B1_ANUENTE, B1_OPC, B1_CODOBS, B1_VLREFUS, B1_IMPORT, B1_FABRIC, B1_SITPROD, B1_MODELO, B1_SETOR, 
                    B1_PRODPAI, B1_BALANCA, B1_TECLA, B1_DESPIMP, B1_TIPOCQ, B1_SOLICIT, B1_GRUPCOM, B1_QUADPRO, 
                    B1_BASE3, B1_DESBSE3, B1_AGREGCU, B1_NUMCQPR, B1_CONTCQP, B1_REVATU, B1_CODEMB, B1_INSS, B1_ESPECIF, 
                    B1_NALNCCA, B1_MAT_PRI, B1_NALSH, B1_REDINSS, B1_REDIRRF, B1_ALADI, B1_TAB_IPI, B1_GRUDES, 
                    B1_DATASUB, B1_REDPIS, B1_REDCOF, B1_PCSLL, B1_PCOFINS, B1_PPIS, B1_MTBF, B1_MTTR, B1_FLAGSUG, 
                    B1_CLASSVE, B1_MIDIA, B1_QTMIDIA, B1_QTDSER, B1_VLR_IPI, B1_ENVOBR, B1_SERIE, B1_FAIXAS, B1_NROPAG, 
                    B1_ISBN, B1_TITORIG, B1_LINGUA, B1_EDICAO, B1_OBSISBN, B1_CLVL, B1_ATIVO, B1_EMAX, B1_PESBRU, 
                    B1_TIPCAR, B1_FRACPER, B1_VLR_ICM, B1_INT_ICM, B1_CORPRI, B1_CORSEC, B1_NICONE, B1_ATRIB1, 
                    B1_ATRIB2, B1_ATRIB3, B1_REGSEQ, B1_VLRSELO, B1_CODNOR, B1_CPOTENC, B1_POTENCI, B1_REQUIS, B1_SELO, 
                    B1_LOTVEN, B1_OK, B1_USAFEFO, B1_QTDACUM, B1_QTDINIC, B1_CNATREC, B1_TNATREC, B1_AFASEMT, B1_AIMAMT, 
                    B1_TERUM, B1_AFUNDES, B1_CEST, B1_GRPCST, B1_IAT, B1_IPPT, B1_GRPNATR, B1_DTFIMNT, B1_DTCORTE, 
                    B1_FECP, B1_MARKUP, B1_CODPROC, B1_LOTESBP, B1_QBP, B1_VALEPRE, B1_CODQAD, B1_AFABOV, B1_VIGENC, 
                    B1_VEREAN, B1_DIFCNAE, B1_ESCRIPI, B1_PMACNUT, B1_PMICNUT, B1_INTEG, B1_HREXPO, B1_CRICMS, 
                    B1_REFBAS, B1_MOPC, B1_USERLGI, B1_USERLGA, B1_UMOEC, B1_UVLRC, B1_PIS, B1_GCCUSTO, B1_CCCUSTO, 
                    B1_TALLA, B1_PARCEI, B1_GDODIF, B1_VLR_PIS, B1_TIPOBN, B1_TPREG, B1_MSBLQL, B1_VLCIF, B1_DCRE, 
                    B1_DCR, B1_DCRII, B1_TPPROD, B1_DCI, B1_COEFDCR, B1_CHASSI, B1_CLASSE, B1_FUSTF, B1_GRPTI, 
                    B1_PRDORI, B1_APOPRO, B1_PRODREC, B1_ALFECOP, B1_ALFECST, B1_CFEMA, B1_FECPBA, B1_MSEXP, B1_PAFMD5, 
                    B1_PRODSBP, B1_CODANT, B1_IDHIST, B1_CRDEST, B1_REGRISS, B1_FETHAB, B1_ESTRORI, B1_CALCFET, 
                    B1_PAUTFET, B1_CARGAE, B1_PRN944I, B1_ALFUMAC, B1_PRINCMG, B1_PR43080, B1_RICM65, B1_SELOEN, 
                    B1_TRIBMUN, B1_RPRODEP, B1_FRETISS, B1_AFETHAB, B1_DESBSE2, B1_BASE2, B1_VLR_COF, B1_PRFDSUL, 
                    B1_TIPVEC, B1_COLOR, B1_RETOPER, B1_COFINS, B1_CSLL, B1_CNAE, B1_ADMIN, B1_AFACS, B1_AJUDIF, 
                    B1_ALFECRN, B1_CFEM, B1_CFEMS, B1_MEPLES, B1_REGESIM, B1_RSATIVO, B1_TFETHAB, B1_TPDP, B1_CRDPRES, 
                    B1_CRICMST, B1_FECOP, B1_CODLAN, B1_GARANT, B1_PERGART, B1_SITTRIB, B1_PORCPRL, B1_IMPNCM, 
                    B1_IVAAJU, B1_BASE, B1_ZZCODAN, B1_ZZNOGRP, B1_ZZOBS1, B1_XFORDEN, B1_ZZMEN1, B1_ZZLEGIS, 
                    D_E_L_E_T_, R_E_C_N_O_, R_E_C_D_E_L_) 
                VALUES(0.0, N'    ', N'{codigo.ljust(15)}', N'{descricao.ljust(100)}', N'{descricao_compl.ljust(60)}', 
                N'                           ', N'{tipo.ljust(2)}', N'{unidade.ljust(2)}', N'{armazem.ljust(2)}', N'{grupo.ljust(4)}', 
                N'{endereco.ljust(6)}', N'          ', N'  ', N'   ', N'   ', 0.0, 0.0, 0.0, N'         ', N'   ', N'   ', 0.0, 
                N'                    ', N'  ', 0.0, N' ', 0.0, N'M', N'               ', 0.0, 0.0, 0.0, 0.0, 
                N'        ', N'        ', 0.0, N'1', N'   ', 0.0, 0.0, N'   ', 0.0, N' ', 0.0, 0.0, 
                N'                    ', 0.0, N'{centro_custo.ljust(9)}', N'         ', N'      ', N'  ', N' ', 1.0, N' ', 
                N'N', N' ', N'  ', N'{data_cadastro.ljust(8)}', N'{data_cadastro.ljust(8)}', N' ', N'N', N' ', 0.0, N'        ', N' ', 0.0, 
                N'      ', N'S', 0.0, N'        ', N' ', 0.0, N'               ', N' ', 0.0, N'   ', N' ', 
                N'          ', N'               ', N'      ', N'N', N'      ', N'      ', N'N', N'  ', N'2', 
                N'                                                                                ', N'      ', 0.0, 
                N'N', N'                    ', N'  ', N'               ', N'  ', N'               ', N' ', N'   ', 
                N'N', N'M', N'N', N'      ', N' ', N'              ', 
                N'                                                            ', N'2', 0.0, 0.0, N'001', 
                N'                              ', N'N', 
                N'                                                                                ', N'       ', 
                N'                    ', N'        ', 0.0, 0.0, N'   ', N'  ', N'   ', N'        ', 0.0, 0.0, 0.0, 
                0.0, 0.0, 0.0, 0.0, N'1', N'1', N'2', 0.0, N'1', 0.0, N'0', N'                    ', 0.0, 0.0, 
                N'          ', N'                                                  ', N'                    ', N'   ', 
                N'                                        ', N'         ', N'S', 0.0, 0.0, N'      ', 0.0, 0.0, 0.0, 
                N'      ', N'      ', N'               ', N'      ', N'      ', N'      ', N'      ', 0.0, N'   ', 
                N'2', 0.0, N' ', N' ', 0.0, N'    ', N'1', 0.0, 0.0, N'   ', N'    ', 0.0, 0.0, N'  ', 0.0, 
                N'         ', N'   ', N' ', N' ', N'  ', N'        ', N'        ', 0.0, 0.0, N'      ', 0.0, 0.0, 
                N' ', N'                      ', 0.0, N'        ', N'  ', N'           ', N'3', 0.0, 0.0, N' ', 
                N'        ', N'0', N' ', NULL, N' 0#  0@< 50A 80; ', N' 0#  0@< 50A 80; ', 0.0, 0.0, N'2', 
                N'        ', N'         ', N'      ', N'      ', N' ', 0.0, N'  ', N' ', N'{'1' if bloquear == 'Sim' else '2'}', 0.0, N'          ', 
                N'         ', 0.0, N'  ', N' ', 0.0, N'                         ', N'      ', N' ', N'    ', 
                N'               ', N' ', N' ', 0.0, 0.0, 0.0, 0.0, N'        ', N'                                ', 
                N'C', N'               ', N'                    ', 0.0, N'  ', N'N', N'               ', N' ', 0.0, 
                N' ', N'S', 0.0, 0.0, 0.0, N'2', N'      ', N'                    ', N' ', N' ', 0.0, 
                N'                                                            ', N'              ', 0.0, 0.0, 
                N'      ', N'          ', N'2', N'2', N'2', N'         ', N'          ', 0.0, N' ', 0.0, N' ', N' ', 
                N' ', N' ', N' ', N' ', N' ', 0.0, N' ', N' ', N'      ', N'2', 0.0, N' ', N'  ', 0.0, N' ', 
                N'              ', N'               ', N'{descricao_grupo.ljust(30)}', NULL, N' ', N'   ', 
                N'{''.ljust(250)}', N' ', N'{chave_primaria}', 0);"""
        return query

    def insert_product(self):
        try:
            self.verify_blank_required_fields()
            if self.required_field_is_blank:
                return

            if self.verificar_se_existe_cadastro(self.ui.codigo_field.text().upper()):
                return
            else:
                with pyodbc.connect(
                        f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}') as conn:
                    query = self.insert_query()
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()

                # Fechar a janela após salvar
                self.accept()

                # save_log_database(self.user_data, selected_row_before_changed, selected_row_after_changed)

                QMessageBox.information(self, f"Eureka® Engenharia",
                                   f"Produto cadastrado com sucesso!\n\n( ͡° ͜ʖ ͡°)")

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Falha ao conectar no banco de dados",
                                        f"Erro ao tentar cadastrar novo produto no TOTVS.\n\n{str(ex)}\n\nContate o "
                                        f"administrador do sistema.")

    def fetch_group_description(self, field_value):
        result = execute_validate_query("grupo", field_value)
        if result is not None:
            group_description = result[1].strip()
            self.ui.desc_grupo_field.setText(group_description)
        else:
            QMessageBox.information(self, "Eureka®",
                                    f"Nenhum resultado encontrado para o campo GRUPO com o valor {field_value}")

    def nova_chave_primaria(self):
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}') as conn:
                query = f"SELECT TOP 1 R_E_C_N_O_ FROM PROTHEUS12_R27.dbo.SB1010 ORDER BY R_E_C_N_O_ DESC;"
                cursor = conn.cursor()
                result = cursor.execute(query).fetchone()

                return result[0] + 1

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Erro ao consultar banco de dados TOTVS",
                                f"Não foi possível obter última chave primária da tabela de produtos SB1010.\n\n{str(ex)}"
                                f"\n\nContate o administrador do sistema.")
            return None
