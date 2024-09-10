def select_query(entity):
    query_dict = {
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
