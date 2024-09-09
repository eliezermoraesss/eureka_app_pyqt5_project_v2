def select_query(entity):
    query_dict = {
        "unidade_medida": f"""
        SELECT 
            AH_UNIMED AS "Código", 
            AH_UMRES AS "Descrição"
        FROM 
            PROTHEUS12_R27.dbo.SAH010
        """
    }
    return query_dict[entity]
