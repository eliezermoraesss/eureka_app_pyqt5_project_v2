def select_query(entity):
    query_dict = {
        "produto": [
            """
            SELECT 
                B1_COD AS "Código", 
                B1_DESC AS "Descrição",
                B1_UM AS "UN."
            FROM
                PROTHEUS12_R27.dbo.SB1010
            WHERE D_E_L_E_T_ <> '*'""",
            """
            SELECT 
                B1_COD AS "Código", 
                B1_DESC AS "Descrição",
                B1_UM AS "UN."
            FROM
                PROTHEUS12_R27.dbo.SB1010
            WHERE 
                B1_COD LIKE ':search_field%'
                AND D_E_L_E_T_ <> '*'""",
            """
            SELECT 
                B1_COD AS "Código", 
                B1_DESC AS "Descrição",
                B1_UM AS "UN."
            FROM
                PROTHEUS12_R27.dbo.SB1010
            WHERE 
                B1_DESC LIKE '%:search_field%'
                AND D_E_L_E_T_ <> '*'"""
        ],
        "qps": ["""
        SELECT 
            cod_qp AS "Código", 
            des_qp AS "Descrição", 
            status_qp AS "Status"
        FROM 
            enaplic_management.dbo.tb_qps
        ORDER BY 
            cod_qp DESC;""",
                """
        SELECT 
            cod_qp AS "Código", 
            des_qp AS "Descrição", 
            status_qp AS "Status"
        FROM 
            enaplic_management.dbo.tb_qps
        WHERE cod_qp LIKE '%:search_field'
        ORDER BY 
            cod_qp DESC;""",
                """
        SELECT 
            cod_qp AS "Código", 
            des_qp AS "Descrição", 
            status_qp AS "Status"
        FROM 
            enaplic_management.dbo.tb_qps
        WHERE des_qp LIKE ':search_field%'
        ORDER BY
            cod_qp DESC;"""],
        "fornecedor": ["""
        SELECT 
            A2_COD AS "Código", 
                    A2_NOME AS "Razão social",
                    A2_NREDUZ AS "Nome fantasia",
                    A2_END AS "Endereço",
                    A2_NR_END AS "Número",
                    A2_BAIRRO AS "Bairro",
                    A2_MUN AS "Município",
                    A2_EST AS "Estado",
                    A2_CEP AS "CEP",
                    A2_CGC AS "CNPJ",
                    A2_INSCR AS "Insc. Estadual",
                    A2_DDD AS "DDD",
                    A2_TEL AS "Telefone",
                    A2_CONTATO AS "Contato",
                    A2_EMAIL AS "E-mail",
                    A2_HPAGE AS "Site",
                    A2_COMPLEM AS "Complemento",
                    A2_ULTCOM AS "Última Compra"
        FROM 
            PROTHEUS12_R27.dbo.SA2010
        WHERE D_E_L_E_T_ <> '*'
        ORDER BY 
            A2_NOME ASC;""",
                       """
               SELECT 
                    A2_COD AS "Código", 
                    A2_NOME AS "Razão social",
                    A2_NREDUZ AS "Nome fantasia",
                    A2_END AS "Endereço",
                    A2_NR_END AS "Número",
                    A2_BAIRRO AS "Bairro",
                    A2_MUN AS "Município",
                    A2_EST AS "Estado",
                    A2_CEP AS "CEP",
                    A2_CGC AS "CNPJ",
                    A2_INSCR AS "Insc. Estadual",
                    A2_DDD AS "DDD",
                    A2_TEL AS "Telefone",
                    A2_CONTATO AS "Contato",
                    A2_EMAIL AS "E-mail",
                    A2_HPAGE AS "Site",
                    A2_COMPLEM AS "Complemento",
                    A2_ULTCOM AS "Última Compra"
                FROM 
                    PROTHEUS12_R27.dbo.SA2010
               WHERE A2_COD LIKE ':search_field%'
               AND D_E_L_E_T_ <> '*'
               ORDER BY 
                   A2_NOME ASC;""",
                       """
               SELECT 
                    A2_COD AS "Código", 
                    A2_NOME AS "Razão social",
                    A2_NREDUZ AS "Nome fantasia",
                    A2_END AS "Endereço",
                    A2_NR_END AS "Número",
                    A2_BAIRRO AS "Bairro",
                    A2_MUN AS "Município",
                    A2_EST AS "Estado",
                    A2_CEP AS "CEP",
                    A2_CGC AS "CNPJ",
                    A2_INSCR AS "Insc. Estadual",
                    A2_DDD AS "DDD",
                    A2_TEL AS "Telefone",
                    A2_CONTATO AS "Contato",
                    A2_EMAIL AS "E-mail",
                    A2_HPAGE AS "Site",
                    A2_COMPLEM AS "Complemento",
                    A2_ULTCOM AS "Última Compra"
                FROM 
                    PROTHEUS12_R27.dbo.SA2010
               WHERE A2_NOME LIKE '%:search_field%'
               ORDER BY
                   A2_NOME ASC;"""],
        "unidade_medida": ["""
                            SELECT 
                                AH_UNIMED AS "Código", 
                                AH_UMRES AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SAH010
                                WHERE D_E_L_E_T_ <> '*'
                            """, """
                            SELECT 
                                AH_UNIMED AS "Código", 
                                AH_UMRES AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SAH010
                            WHERE AH_UNIMED LIKE ':search_field%'
                            AND D_E_L_E_T_ <> '*'""", """
                            SELECT 
                                AH_UNIMED AS "Código", 
                                AH_UMRES AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SAH010
                            WHERE AH_UMRES LIKE '%:search_field%'
                            AND D_E_L_E_T_ <> '*'"""
                           ],
        "tipo": ["""
                            SELECT
                                X5_CHAVE AS "Código",
                                X5_DESCRI AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SX5010
                            WHERE 
                                X5_TABELA = '02'
                            AND 
                                D_E_L_E_T_ <> '*'
                            """, """
                            SELECT
                                X5_CHAVE AS "Código",
                                X5_DESCRI AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SX5010
                            WHERE 
                                X5_TABELA = '02'
                            AND 
                                X5_CHAVE LIKE ':search_field%'
                            AND 
                                D_E_L_E_T_ <> '*'""", """
                            SELECT
                                X5_CHAVE AS "Código",
                                X5_DESCRI AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SX5010
                            WHERE 
                                X5_TABELA = '02'
                            AND 
                                X5_DESCRI LIKE '%:search_field%'
                            AND 
                                D_E_L_E_T_ <> '*'"""
                 ],
        "armazem": ["""
                            SELECT 
                                NNR_CODIGO AS "Código", 
                                NNR_DESCRI AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.NNR010
                                WHERE D_E_L_E_T_ <> '*'
                            """, """
                            SELECT 
                                NNR_CODIGO AS "Código", 
                                NNR_DESCRI AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.NNR010
                            WHERE NNR_CODIGO LIKE ':search_field%'
                            AND D_E_L_E_T_ <> '*'""", """
                            SELECT 
                                NNR_CODIGO AS "Código", 
                                NNR_DESCRI AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.NNR010
                            WHERE NNR_DESCRI LIKE '%:search_field%'
                            AND D_E_L_E_T_ <> '*'"""
                    ],
        "centro_custo": ["""
                            SELECT 
                                CTT_CUSTO AS "Código", 
                                CTT_DESC01 AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.CTT010
                                WHERE D_E_L_E_T_ <> '*'
                            """, """
                            SELECT 
                                CTT_CUSTO AS "Código", 
                                CTT_DESC01 AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.CTT010
                            WHERE CTT_CUSTO LIKE ':search_field%'
                            AND D_E_L_E_T_ <> '*'""", """
                            SELECT 
                                CTT_CUSTO AS "Código", 
                                CTT_DESC01 AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.CTT010
                            WHERE CTT_DESC01 LIKE '%:search_field%'
                            AND D_E_L_E_T_ <> '*'"""
                         ],
        "grupo": ["""
                            SELECT 
                                BM_GRUPO AS "Código", 
                                BM_DESC AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SBM010
                                WHERE D_E_L_E_T_ <> '*'
                            """, """
                            SELECT 
                                BM_GRUPO AS "Código", 
                                BM_DESC AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SBM010
                            WHERE BM_GRUPO LIKE ':search_field%'
                            AND D_E_L_E_T_ <> '*'""", """
                            SELECT 
                                BM_GRUPO AS "Código", 
                                BM_DESC AS "Descrição"
                            FROM 
                                PROTHEUS12_R27.dbo.SBM010
                            WHERE BM_DESC LIKE '%:search_field%'
                            AND D_E_L_E_T_ <> '*'"""
                  ]
    }
    return query_dict[entity]
