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
                           ]
    }
    return query_dict[entity]
