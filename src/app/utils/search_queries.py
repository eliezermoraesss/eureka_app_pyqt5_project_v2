def select_query(entity):
    query_dict = {
        "unidade_medida": ["""
            SELECT 
                AH_UNIMED AS "Código", 
                AH_UMRES AS "Descrição"
            FROM 
                PROTHEUS12_R27.dbo.SAH010
            """, """
            SELECT 
                AH_UNIMED AS "Código", 
                AH_UMRES AS "Descrição"
            FROM 
                PROTHEUS12_R27.dbo.SAH010
            WHERE AH_UNIMED LIKE ':search_field%'""",
                               """
            SELECT 
                AH_UNIMED AS "Código", 
                AH_UMRES AS "Descrição"
            FROM 
                PROTHEUS12_R27.dbo.SAH010
            WHERE AH_UMRES LIKE '%:search_field%'"""
                           ]
    }
    return query_dict[entity]
