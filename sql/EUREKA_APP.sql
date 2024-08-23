-- QUERY ONDE O PRODUTO É USADO?
  SELECT STRUT.G1_COD AS "Código", PROD.B1_DESC "Descrição" 
                    FROM PROTHEUS12_R27.dbo.SG1010 STRUT 
                    INNER JOIN PROTHEUS12_R27.dbo.SB1010 PROD 
                    ON G1_COD = B1_COD WHERE G1_COMP = 'C-006-041-306' 
                    AND STRUT.G1_REVFIM <> 'ZZZ' AND STRUT.D_E_L_E_T_ <> '*'
                    AND STRUT.G1_REVFIM = (SELECT MAX(G1_REVFIM) 
                                            FROM PROTHEUS12_R27.dbo.SG1010 
                                            WHERE 
                                                G1_COD = 'C-006-041-306' 
                                                AND G1_REVFIM <> 'ZZZ' 
                                                AND STRUT.D_E_L_E_T_ <> '*');
                                               
                                               
                                               
SELECT STRUT.G1_COD AS "Código", PROD.B1_DESC "Descrição" 
                    FROM PROTHEUS12_R27.dbo.SG1010 STRUT 
                    INNER JOIN PROTHEUS12_R27.dbo.SB1010 PROD 
                    ON G1_COD = B1_COD WHERE G1_COMP = 'E6126-005-020' 
                    AND STRUT.G1_REVFIM <> 'ZZZ' AND STRUT.D_E_L_E_T_ <> '*'
                    AND STRUT.G1_REVFIM = (SELECT MAX(G1_REVFIM) 
                                            FROM PROTHEUS12_R27.dbo.SG1010 
                                            WHERE 
                                                G1_COD = 'E6126-005-020' 
                                                AND G1_REVFIM <> 'ZZZ' 
                                                AND STRUT.D_E_L_E_T_ <> '*');

SELECT 
	SC.C1_ZZNUMQP AS "QP",
	SC.C1_NUM AS "SC",
	SC.C1_ITEM AS "Item SC",
	SC.C1_QUANT AS "Qtd. SC",
	SC.C1_PEDIDO AS "Ped. Compra",
	SC.C1_ITEMPED AS "Item Ped.",
	PC.C7_QUANT AS "Qtd. Ped.",
	PC.C7_PRECO AS "Preço Unit. (R$)",
	PC.C7_TOTAL AS "Sub-total (R$)",
	PC.C7_DATPRF AS "Previsão Entrega",
	ITEM_NF.D1_DOC AS "Nota Fiscal Ent.",
	ITEM_NF.D1_QUANT AS "Qtd. Entregue",
	CASE 
	    WHEN ITEM_NF.D1_QUANT IS NULL THEN SC.C1_QUJE 
	    ELSE SC.C1_QUJE - ITEM_NF.D1_QUANT
	END AS "Qtd. Pendente",
	ITEM_NF.D1_DTDIGIT AS "Data Entrega",
	PC.C7_ENCER AS "Status Ped. Compra",
	SC.C1_PRODUTO AS "Código",
	SC.C1_DESCRI AS "Descrição",
	SC.C1_UM AS "UM",
	PROD.B1_ZZLOCAL AS "Endereço:",
	SC.C1_EMISSAO AS "Emissão SC",
	PC.C7_EMISSAO AS "Emissão PC",
	ITEM_NF.D1_EMISSAO AS "Emissão NF",
	SC.C1_ORIGEM AS "Origem",
	SC.C1_OBS AS "Observação",
	SC.C1_LOCAL AS "Cod. Armazém",
	ARM.NNR_DESCRI AS "Desc. Armazém",
	SC.C1_IMPORT AS "Importado?",
	PC.C7_OBS AS "Observações",
	PC.C7_OBSM AS "Observações item",
	FORN.A2_COD AS "Cód. Forn.",
	FORN.A2_NOME AS "Raz. Soc. Forn.",
	FORN.A2_NREDUZ AS "Nom. Fantasia Forn.",
	US.USR_NOME AS "Solicitante",
	PC.S_T_A_M_P_ AS "Aberto em:",
	SC.C1_OP AS "OP"
	FROM 
	    PROTHEUS12_R27.dbo.SC7010 PC
	LEFT JOIN 
	    PROTHEUS12_R27.dbo.SD1010 ITEM_NF
	ON 
	    PC.C7_NUM = ITEM_NF.D1_PEDIDO AND PC.C7_ITEM = ITEM_NF.D1_ITEMPC
	LEFT JOIN
	    PROTHEUS12_R27.dbo.SC1010 SC
	ON 
	    SC.C1_PEDIDO = PC.C7_NUM AND SC.C1_ITEMPED = PC.C7_ITEM
	LEFT JOIN
	    PROTHEUS12_R27.dbo.SA2010 FORN
	ON
	    FORN.A2_COD = PC.C7_FORNECE 
	LEFT JOIN
	    PROTHEUS12_R27.dbo.NNR010 ARM
	ON
	    SC.C1_LOCAL = ARM.NNR_CODIGO
	LEFT JOIN 
	    PROTHEUS12_R27.dbo.SYS_USR US
	ON
	    SC.C1_SOLICIT = US.USR_CODIGO AND US.D_E_L_E_T_ <> '*'
	INNER JOIN 
	    PROTHEUS12_R27.dbo.SB1010 PROD
	ON 
	    PROD.B1_COD = SC.C1_PRODUTO
	WHERE 
	    PC.C7_NUM LIKE '%'
		AND PC.C7_NUMSC LIKE '%'
		AND PC.C7_ZZNUMQP LIKE '%6963'
		AND PC.C7_PRODUTO LIKE '%'
		AND PC.C7_DESC LIKE '%'
		AND PC.C7_DESC LIKE '%%'
		AND SC.C1_OP LIKE '%' 
		AND FORN.A2_NOME LIKE '%'
		AND FORN.A2_NREDUZ LIKE '%%'
		AND SC.C1_LOCAL LIKE '%' 
		AND C1_EMISSAO >= '20180628' AND C1_EMISSAO <= '20240704'
		AND PC.D_E_L_E_T_ <> '*'
		AND SC.D_E_L_E_T_ <> '*'
		AND PROD.D_E_L_E_T_ <> '*'
		
	UNION ALL
	
	SELECT 
		SC.C1_ZZNUMQP AS "QP",
		SC.C1_NUM AS "SC",
		SC.C1_ITEM AS "Item SC",
		SC.C1_QUANT AS "Qtd. SC",
		NULL AS "Ped. Compra",
		NULL AS "Item Ped.",
		NULL AS "Qtd. Ped.",
		NULL AS "Preço Unit. (R$)",
		NULL AS "Sub-total (R$)",
		NULL AS "Previsão Entrega",
		NULL AS "Nota Fiscal Ent.",
		NULL AS "Qtd. Entregue",
		NULL AS "Qtd. Pendente",
		NULL AS "Data Entrega",
		NULL AS "Status Ped. Compra",
		SC.C1_PRODUTO AS "Código",
		SC.C1_DESCRI AS "Descrição",
		SC.C1_UM AS "UM",
		PROD.B1_ZZLOCAL AS "Endereço:",
		SC.C1_EMISSAO AS "Emissão SC",
		NULL AS "Emissão PC",
		NULL AS "Emissão NF",
		SC.C1_ORIGEM AS "Origem",
		SC.C1_OBS AS "Observação",
		SC.C1_LOCAL AS "Cod. Armazém",
		ARM.NNR_DESCRI AS "Desc. Armazém",
		SC.C1_IMPORT AS "Importado?",
		NULL AS "Observações",
		NULL AS "Observações item",
		NULL AS "Cód. Forn.",
		NULL AS "Raz. Soc. Forn.",
		NULL AS "Nom. Fantasia Forn.",
		US.USR_NOME AS "Solicitante",
		NULL AS "Aberto em:",
		SC.C1_OP AS "OP"
		FROM 
		    PROTHEUS12_R27.dbo.SC1010 SC
		LEFT JOIN
		    PROTHEUS12_R27.dbo.NNR010 ARM
		ON 
		    SC.C1_LOCAL = ARM.NNR_CODIGO
		LEFT JOIN 
		    PROTHEUS12_R27.dbo.SYS_USR US
		ON 
		    SC.C1_SOLICIT = US.USR_CODIGO AND US.D_E_L_E_T_ <> '*'
		INNER JOIN 
		    PROTHEUS12_R27.dbo.SB1010 PROD
		ON 
		    PROD.B1_COD = SC.C1_PRODUTO
		WHERE 
		    SC.C1_PEDIDO LIKE '      %'

		AND SC.C1_NUM LIKE '%'
		AND SC.C1_ZZNUMQP LIKE '%6963'
		AND SC.C1_PRODUTO LIKE '%'
		AND SC.C1_DESCRI LIKE '%'
		AND SC.C1_DESCRI LIKE '%%'
		AND SC.C1_OP LIKE '%'
		AND SC.C1_LOCAL LIKE '%'
		AND SC.D_E_L_E_T_ <> '*'
		AND SC.C1_COTACAO <> 'XXXXXX'
		AND C1_EMISSAO >= '20200628' AND C1_EMISSAO <= '20240704'
		AND PROD.D_E_L_E_T_ <> '*'
		ORDER BY "SC" DESC;


DECLARE @CodigoPai VARCHAR(50) = 'M-059-201-160'; -- Substitua pelo código pai que deseja consultar

-- CTE para selecionar os itens pai e seus subitens recursivamente
WITH ListMP AS (
    -- Selecionar o item pai inicialmente
    SELECT G1_COD AS "CÓDIGO", G1_COMP AS "COMPONENTE", G1_QUANT AS "QUANTIDADE", 0 AS Nivel
    FROM SG1010
    WHERE G1_COD = @CodigoPai AND G1_REVFIM = (
        SELECT MAX(G1_REVFIM) 
        FROM SG1010 
        WHERE G1_COD = @CodigoPai AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'
    ) AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'

    UNION ALL

    -- Selecione os subitens de cada item pai e multiplique as quantidades
    SELECT sub.G1_COD, sub.G1_COMP, sub.G1_QUANT * pai.QUANTIDADE, pai.Nivel + 1
    FROM SG1010 AS sub
    INNER JOIN ListMP AS pai ON sub.G1_COD = pai."COMPONENTE"
    WHERE pai.Nivel < 100 -- Defina o limite máximo de recursão aqui
    AND sub.G1_REVFIM <> 'ZZZ' AND sub.D_E_L_E_T_ <> '*'
)

-- Selecione todas as matérias-primas (tipo = 'MP') que correspondem aos itens encontrados e some as quantidades
SELECT 
    mat.G1_COD AS "CODIGO PAI",
    mat.G1_COMP AS "CÓDIGO", 
    prod.B1_DESC AS "DESCRIÇÃO", 
    SUM(pai.QUANTIDADE) AS "QUANT.",
    mat.G1_XUM AS "UNID. MED.", 
    prod.B1_UCOM AS "ULT. ATUALIZ.",
    prod.B1_TIPO AS "TIPO", 
    prod.B1_LOCPAD AS "ARMAZÉM", 
    prod.B1_UPRC AS "VALOR UNIT. (R$)",
    SUM(pai.QUANTIDADE * prod.B1_UPRC) AS "SUB-TOTAL (R$)"
FROM SG1010 AS mat
INNER JOIN ListMP AS pai ON mat.G1_COD = pai."CÓDIGO"
INNER JOIN SB1010 AS prod ON mat.G1_COMP = prod.B1_COD
WHERE prod.B1_TIPO = 'MP'
AND prod.B1_LOCPAD IN ('01','03', '11', '12', '97')
AND mat.G1_REVFIM <> 'ZZZ' 
AND mat.D_E_L_E_T_ <> '*'
GROUP BY 
    mat.G1_COD, 
    mat.G1_COMP, 
    prod.B1_DESC, 
    mat.G1_XUM, 
    prod.B1_UCOM, 
    prod.B1_TIPO, 
    prod.B1_LOCPAD, 
    prod.B1_UPRC
ORDER BY mat.G1_COMP ASC;




fix: recursive query was modified. CTE (Common Table Expression) to multiply the quantity of each level and sum them in the final


-- QUERY DE RECURSIVIDADE NA TABELA DE ESTRUTURA DE PRODUTO

DECLARE @CodigoPai VARCHAR(50) = 'M-059-201-999'; -- Substitua pelo código pai que deseja consultar

    -- CTE para selecionar os itens pai e seus subitens recursivamente
    WITH ListMP AS (
        -- Selecionar o item pai inicialmente
        SELECT G1_COD AS "CÓDIGO", G1_COMP AS "COMPONENTE", G1_QUANT AS "QUANTIDADE", 0 AS Nivel
        FROM SG1010
        WHERE G1_COD = @CodigoPai AND G1_REVFIM = (
            SELECT MAX(G1_REVFIM) 
            FROM SG1010 
            WHERE G1_COD = @CodigoPai AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'
        ) AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'

        UNION ALL

        -- Selecione os subitens de cada item pai e multiplique as quantidades
        SELECT sub.G1_COD, sub.G1_COMP, sub.G1_QUANT * pai.QUANTIDADE, pai.Nivel + 1
        FROM SG1010 AS sub
        INNER JOIN ListMP AS pai ON sub.G1_COD = pai."COMPONENTE"
        WHERE pai.Nivel < 100 -- Defina o limite máximo de recursão aqui
        AND sub.G1_REVFIM <> 'ZZZ' AND sub.D_E_L_E_T_ <> '*'
    )
    
    -- Selecionar os componentes, somar as quantidades e evitar componentes duplicados
    SELECT 
        "COMPONENTE" AS "CÓDIGO",
        prod.B1_DESC AS "DESCRIÇÃO",
        SUM("QUANTIDADE") AS "QUANT.",
        prod.B1_UM AS "UNID. MED.", 
        prod.B1_UCOM AS "ULT. ATUALIZ.",
        prod.B1_TIPO AS "TIPO", 
        prod.B1_LOCPAD AS "ARMAZÉM", 
        prod.B1_UPRC AS "VALOR UNIT. (R$)",
        SUM("QUANTIDADE" * prod.B1_UPRC) AS "SUB-TOTAL (R$)"
    FROM 
        ListMP AS listMP
    INNER JOIN 
        SB1010 AS prod ON listMP."COMPONENTE" = prod.B1_COD
    WHERE 
        prod.B1_TIPO = 'MP'
        AND prod.B1_LOCPAD IN ('01','03', '11', '12', '97')
        AND prod.D_E_L_E_T_ <> '*'
    GROUP BY 
        "COMPONENTE",
        prod.B1_DESC,
        prod.B1_UM,
        prod.B1_UCOM,
        prod.B1_TIPO,
        prod.B1_LOCPAD,
        prod.B1_UPRC
    ORDER BY 
        "COMPONENTE" ASC;

    -- EXIBE O NÍVEL DOS COMPONENTES
    SELECT "COMPONENTE", "QUANTIDADE", Nivel FROM ListMP ORDER BY "COMPONENTE" ASC
