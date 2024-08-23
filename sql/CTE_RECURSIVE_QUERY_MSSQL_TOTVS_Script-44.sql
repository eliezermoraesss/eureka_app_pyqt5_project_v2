DECLARE @CodigoPai VARCHAR(50) = 'M-039-033-992'; -- Substitua pelo código pai que deseja consultar

    -- CTE para selecionar os itens pai e seus subitens recursivamente
    WITH ListMP AS (
-- Selecionar o item pai inicialmente
SELECT
	G1_COD AS "CÓDIGO",
	G1_COMP AS "COMPONENTE",
	G1_QUANT AS "QUANTIDADE",
	0 AS Nivel,
	G1_REVFIM AS "REVISAO"
FROM
	SG1010
WHERE
	G1_COD = @CodigoPai
	AND G1_REVFIM = (
	SELECT
		MAX(G1_REVFIM)
	FROM
		SG1010
	WHERE
		G1_COD = @CodigoPai
		AND G1_REVFIM <> 'ZZZ'
		AND D_E_L_E_T_ <> '*'
        )
	AND G1_REVFIM <> 'ZZZ'
	AND D_E_L_E_T_ <> '*'
UNION ALL
-- Selecione os subitens de cada item pai e multiplique as quantidades
SELECT
	filho.G1_COD,
	filho.G1_COMP,
	filho.G1_QUANT * pai.QUANTIDADE,
	pai.Nivel + 1,
	filho.G1_REVFIM
FROM
	SG1010 AS filho
INNER JOIN ListMP AS pai ON
	filho.G1_COD = pai."COMPONENTE"
WHERE
	pai.Nivel < 100
	-- Defina o limite máximo de recursão aqui
	AND filho.G1_REVFIM <> 'ZZZ'
	AND filho.D_E_L_E_T_ <> '*'
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
	   
-- ************************************************************************************************************************************
	   
DECLARE @CodigoPai VARCHAR(50) = 'M-039-033-992'; -- Substitua pelo código pai que deseja consultar

    -- CTE para selecionar os itens pai e seus subitens recursivamente
    WITH ListMP AS (
-- Selecionar o item pai inicialmente
SELECT
	G1_COD AS "CÓDIGO",
	G1_COMP AS "COMPONENTE",
	G1_QUANT AS "QUANTIDADE",
	0 AS Nivel,
	G1_REVFIM AS "REVISAO"
FROM
	SG1010
WHERE
	G1_COD = @CodigoPai
	AND G1_REVFIM = (
	SELECT
		MAX(G1_REVFIM)
	FROM
		SG1010
	WHERE
		G1_COD = @CodigoPai
		AND G1_REVFIM <> 'ZZZ'
		AND D_E_L_E_T_ <> '*'
        )
	AND G1_REVFIM <> 'ZZZ'
	AND D_E_L_E_T_ <> '*'
UNION ALL
-- Selecione os subitens de cada item pai e multiplique as quantidades
SELECT
	sub.G1_COD,
	sub.G1_COMP,
	sub.G1_QUANT * pai.QUANTIDADE,
	pai.Nivel + 1,
	G1_REVFIM AS "REVISAO"
FROM
	SG1010 AS sub
INNER JOIN ListMP AS pai ON
	sub.G1_COD = pai."COMPONENTE"
WHERE
	pai.Nivel < 100
	-- Defina o limite máximo de recursão aqui
	AND sub.G1_REVFIM <> 'ZZZ'
	AND sub.D_E_L_E_T_ <> '*'
    )
    
    -- EXIBE O NÍVEL DOS COMPONENTES
    SELECT "COMPONENTE", "QUANTIDADE", Nivel, REVISAO FROM ListMP;
   
-- ************************************************************************************************************************************
   
DECLARE @CodigoPai VARCHAR(50) = 'M-039-033-992'; -- Substitua pelo código pai que deseja consultar

-- CTE para selecionar as revisões máximas
WITH MaxRevisoes AS (
    SELECT
        G1_COD,
        MAX(G1_REVFIM) AS MaxRevisao
    FROM
        SG1010
    WHERE
        G1_REVFIM <> 'ZZZ'
        AND D_E_L_E_T_ <> '*'
    GROUP BY
        G1_COD
),
-- CTE para selecionar os itens pai e seus subitens recursivamente
ListMP AS (
    -- Selecionar o item pai inicialmente
    SELECT
        G1.G1_COD AS "CÓDIGO",
        G1.G1_COMP AS "COMPONENTE",
        G1.G1_QUANT AS "QUANTIDADE",
        0 AS Nivel,
        G1.G1_REVFIM AS "REVISAO"
    FROM
        SG1010 G1
    INNER JOIN MaxRevisoes MR ON G1.G1_COD = MR.G1_COD AND G1.G1_REVFIM = MR.MaxRevisao
    WHERE
        G1.G1_COD = @CodigoPai
        AND G1.G1_REVFIM <> 'ZZZ'
        AND G1.D_E_L_E_T_ <> '*'
    UNION ALL
    -- Selecione os subitens de cada item pai e multiplique as quantidades
    SELECT
        filho.G1_COD,
        filho.G1_COMP,
        filho.G1_QUANT * pai.QUANTIDADE,
        pai.Nivel + 1,
        filho.G1_REVFIM
    FROM
        SG1010 AS filho
    INNER JOIN ListMP AS pai ON
        filho.G1_COD = pai."COMPONENTE"
    INNER JOIN MaxRevisoes MR ON filho.G1_COD = MR.G1_COD AND filho.G1_REVFIM = MR.MaxRevisao
    WHERE
        pai.Nivel < 100
        -- Defina o limite máximo de recursão aqui
        AND filho.G1_REVFIM <> 'ZZZ'
        AND filho.D_E_L_E_T_ <> '*'
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

