from datetime import datetime

from src.app.utils.utils import tratar_campo_codigo, formatar_campo


def insert_query(self):
    codigo = tratar_campo_codigo(self.ui.codigo_field)
    descricao = formatar_campo(self.ui.descricao_field)
    descricao_compl = formatar_campo(self.ui.desc_comp_field)
    tipo = formatar_campo(self.ui.tipo_field)
    unidade = formatar_campo(self.ui.um_field)
    armazem = formatar_campo(self.ui.armazem_field)
    grupo = formatar_campo(self.ui.grupo_field)
    descricao_grupo = formatar_campo(self.ui.desc_grupo_field)
    centro_custo = formatar_campo(self.ui.cc_field)
    bloquear = self.ui.bloquear_combobox.currentText()
    endereco = formatar_campo(self.ui.endereco_field)

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
<<<<<<< HEAD
                N'2', 0.0, N' ', N' ', 0.0, N'  N' ', N' ', N'  ', N'        ', N'        ', 0.0, 0.0, N'      ', 0.0, 0.0, 
                N' ', N'                ', N'1', 0.0, 0.0, N'   ', N'    ', 0.0, 0.0, N'  ', 0.0, 
                N'         ', N'   ',         ', 0.0, N'        ', N'  ', N'           ', N'3', 0.0, 0.0, N' ', 
=======
                N'2', 0.0, N' ', N' ', 0.0, N'    ', N'1', 0.0, 0.0, N'   ', N'    ', 0.0, 0.0, N'  ', 0.0, 
                N'         ', N'   ', N' ', N' ', N'  ', N'        ', N'        ', 0.0, 0.0, N'      ', 0.0, 0.0, 
                N' ', N'                      ', 0.0, N'        ', N'  ', N'           ', N'3', 0.0, 0.0, N' ', 
>>>>>>> eureka/improvements
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
