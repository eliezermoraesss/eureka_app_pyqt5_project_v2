SELECT * FROM sysobjects WHERE name='eureka_users' AND xtype='U'
SELECT * FROM sysobjects WHERE name='eureka_password_reset' AND xtype='U'

SELECT
    DB_NAME(database_id) AS DatabaseName,
    type_desc AS FileType,
    size / 128.0 AS TotalSizeMB,
    size / 128.0 - CAST(FILEPROPERTY(name, 'SpaceUsed') AS INT) / 128.0 AS FreeSpaceMB
FROM sys.master_files
WHERE DB_NAME(database_id) = 'enaplic_management';  -- Substitua pelo nome do banco de dados

EXEC sp_spaceused;
EXEC sp_spaceused 'tb_baseline';
EXEC xp_fixeddrives;

SELECT * FROM enaplic_management.dbo.eureka_users;

SELECT * FROM enaplic_management.dbo.eureka_password_reset;

SELECT * FROM enaplic_management.dbo.tb_dashboard_indicators;

SELECT * FROM enaplic_management.dbo.tb_qps;

SELECT * FROM enaplic_management.dbo.tb_user_logs;

SELECT * FROM enaplic_management.dbo.tb_user_logs
WHERE full_name LIKE 'Rafael%';

SELECT * FROM enaplic_management.dbo.tb_user_logs
WHERE part_number LIKE 'M-034-015-148%';

SELECT * FROM enaplic_management.dbo.tb_baseline;

SELECT COUNT(*) FROM enaplic_management.dbo.tb_baseline WHERE cod_qp = '007933';

SELECT * FROM enaplic_management.dbo.tb_baseline WHERE cod_qp = '007933';

DELETE FROM enaplic_management.dbo.tb_baseline WHERE cod_qp = '007933';

-- DROP TABLE enaplic_management.dbo.tb_baseline;

-- DELETE FROM enaplic_management.dbo.tb_baseline;

CREATE TABLE enaplic_management.dbo.tb_baseline (
	id INT IDENTITY(1,1) PRIMARY KEY,
    cod_qp VARCHAR(6) NOT NULL,
    equipamento VARCHAR(200),
    grupo VARCHAR(100),
    nivel VARCHAR(2),
    codigo VARCHAR(15),
    codigo_pai VARCHAR(15),
    descricao VARCHAR(200),
    tipo VARCHAR(2),
    qtde_bl DECIMAL(12, 5),
   	unid_medida VARCHAR(2),
    especificacoes VARCHAR(100),
    qtde_proj DECIMAL(12, 5),
    qtde_total DECIMAL(12, 5),
    status VARCHAR(30),
    status_op VARCHAR(30),
    created_at DATETIME DEFAULT switchoffset(sysdatetimeoffset(), '-03:00') NOT NULL
);

-- DROP TABLE enaplic_management.dbo.eureka_users;

CREATE TABLE enaplic_management.dbo.eureka_users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                full_name NVARCHAR(100) NOT NULL,
                username NVARCHAR(20) NOT NULL UNIQUE,
                email NVARCHAR(50) NOT NULL UNIQUE,
                hashed_password NVARCHAR(60) NOT NULL,
                role NVARCHAR(50) NOT NULL,
                created_at DATETIME DEFAULT switchoffset(sysdatetimeoffset(), '-03:00') NOT NULL
                )
                
ALTER TABLE enaplic_management.dbo.eureka_users
ALTER COLUMN hashed_password NVARCHAR(60) NOT NULL

DELETE FROM enaplic_management.dbo.eureka_users

-- DROP TABLE enaplic_management.dbo.eureka_password_reset;
                
CREATE TABLE enaplic_management.dbo.eureka_password_reset (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id INT NOT NULL,
                reset_code NVARCHAR(6) NOT NULL,
                expiration_time DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES dbo.eureka_users(id)
                )
                
DELETE FROM enaplic_management.dbo.eureka_password_reset

-- DROP TABLE enaplic_management.dbo.tb_user_logs;

CREATE TABLE enaplic_management.dbo.tb_user_logs (
    id INT IDENTITY(1,1) NOT NULL,                -- Identificador único
    full_name NVARCHAR(100) NOT NULL,             -- Nome completo
    email NVARCHAR(50) NOT NULL,                 -- Endereço de e-mail
   	user_role NVARCHAR(20) NOT NULL,			-- Perfil de acesso
   	part_number NVARCHAR(15) NOT NULL,			-- Código do produto
    log_description NVARCHAR(500) NULL,                -- Campo de observação, pode ser nulo
    created_at DATETIME DEFAULT switchoffset(sysdatetimeoffset(), '-03:00') NOT NULL, -- Data e hora de criação
    PRIMARY KEY (id)                              -- Definir o campo id como chave primária
);

ALTER TABLE enaplic_management.dbo.tb_user_logs
ALTER COLUMN log_description NVARCHAR()

DELETE FROM enaplic_management.dbo.tb_user_logs

-- DROP TABLE enaplic_management.dbo.tb_open_qps;

-- enaplic_management.dbo.tb_qps definição

-- Drop table

-- DROP TABLE enaplic_management.dbo.tb_qps;

CREATE TABLE enaplic_management.dbo.tb_qps (
	id int IDENTITY(1,1) NOT NULL,
	cod_qp varchar(6) NOT NULL PRIMARY KEY,
	des_qp varchar(200) NOT NULL,
	status_qp char(1) NOT NULL,
	dt_open_qp varchar(10) NULL,
	dt_end_qp varchar(10) NULL,
	dt_completed_qp varchar(10) NULL,
	vl_delay int NULL,
	status_delivery varchar(50) NULL,
	S_T_A_M_P datetime DEFAULT switchoffset(sysdatetimeoffset(),'-03:00') NOT NULL
);

-- CREATE DATABASE enaplic_management;

-- DROP DATABASE enaplic_management;

-- USE enaplic_management;
-- USE master;

-- DROP TABLE enaplic_management.dbo.tb_dashboard_indicators;

CREATE TABLE enaplic_management.dbo.tb_dashboard_indicators (
	id bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
	cod_qp varchar(6) NOT NULL,
	des_qp varchar(200) NOT NULL,
	status_qp char(1) NOT NULL,
	dt_open_qp varchar(10) NULL,
	dt_end_qp varchar(10) NULL,
	dt_start_proj varchar(10) NULL,
	dt_end_proj varchar(10) NULL,
	vl_proj_duration int NULL,
	status_proj varchar(1) NULL,
	vl_proj_all_prod int NOT NULL,
	vl_proj_prod_cancel int NOT NULL,
	vl_proj_modify_perc decimal(8,2) NOT NULL,
	vl_proj_released int NOT NULL,
	vl_proj_finished int NOT NULL,
	vl_proj_adjusted int NOT NULL,
	vl_proj_pi int NOT NULL,
	vl_proj_mp int NOT NULL,
	vl_all_op int NOT NULL,
	vl_pcp_perc decimal(8,2) NOT NULL,
	vl_closed_op int NOT NULL,
	vl_product_perc decimal(8,2) NULL,
	vl_all_sc int NOT NULL,
	vl_all_pc int NOT NULL,
	vl_compras_perc decimal(8,2) NOT NULL,
	vl_mat_received int NOT NULL,
	vl_mat_received_perc decimal(8,2) NOT NULL,
	vl_total_mp_pc_cost decimal(12,2) NOT NULL,
	vl_mp_pc_cost decimal(12,2) NOT NULL,
	vl_com_pc_cost decimal(12,2) NOT NULL,
	vl_mp_deliver_cost decimal(12,2) NOT NULL,
	vl_com_deliver_cost decimal(12,2) NOT NULL,
	S_T_A_M_P datetime DEFAULT switchoffset(sysdatetimeoffset(),'-03:00') NOT NULL
);

-- DROP TABLE enaplic_management.dbo.tb_dashboard_indicators_test;

CREATE TABLE enaplic_management.dbo.tb_dashboard_indicators_test (
	id bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
	cod_qp varchar(6) NOT NULL,
	des_qp varchar(200) NOT NULL,
	status_qp char(1) NOT NULL,
	dt_open_qp varchar(10) NULL,
	dt_end_qp varchar(10) NULL,
	dt_start_proj varchar(10) NULL,
	dt_end_proj varchar(10) NULL,
	vl_proj_duration int NULL,
	status_proj varchar(1) NULL,
	vl_proj_all_prod int NOT NULL,
	vl_proj_prod_cancel int NOT NULL,
	vl_proj_modify_perc decimal(8,2) NOT NULL,
	vl_proj_released int NOT NULL,
	vl_proj_finished int NOT NULL,
	vl_proj_adjusted int NOT NULL,
	vl_proj_pi int NOT NULL,
	vl_proj_mp int NOT NULL,
	vl_all_op int NOT NULL,
	vl_pcp_perc decimal(8,2) NOT NULL,
	vl_closed_op int NOT NULL,
	vl_product_perc decimal(8,2) NULL,
	vl_all_sc int NOT NULL,
	vl_all_pc int NOT NULL,
	vl_compras_perc decimal(8,2) NOT NULL,
	vl_mat_received int NOT NULL,
	vl_mat_received_perc decimal(8,2) NOT NULL,
	vl_total_mp_pc_cost decimal(12,2) NOT NULL,
	vl_mp_pc_cost decimal(12,2) NOT NULL,
	vl_com_pc_cost decimal(12,2) NOT NULL,
	vl_mp_deliver_cost decimal(12,2) NOT NULL,
	vl_com_deliver_cost decimal(12,2) NOT NULL,
	S_T_A_M_P datetime DEFAULT switchoffset(sysdatetimeoffset(),'-03:00') NOT NULL
);


INSERT INTO 
	enaplic_management.dbo.tb_dashboard_indicators 
    (cod_qp, des_qp, dt_open_qp, dt_end_qp, status_proj, vl_proj_all_prod, 
    vl_proj_prod_cancel, vl_proj_modify_perc, vl_proj_released, 
    vl_proj_finished, vl_proj_adjusted, vl_proj_pi, vl_proj_mp, 
    vl_all_op, vl_pcp_perc, vl_closed_op, vl_product_perc, 
    vl_all_sc, vl_all_pc, vl_compras_perc, vl_mat_received, 
    vl_mat_received_perc) 
VALUES
    (N'007668', 'TESTE', '22/07/2024', '22/07/2024', 'A', 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    
INSERT INTO 
	enaplic_management.dbo.tb_open_qps
   	(cod_qp, des_qp, dt_open_qp, dt_end_qp) 
VALUES('007668', 'teste', '11/07/2024', '11/08/2024');

--005552
--006963
--007047
--007668

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators 
ADD CONSTRAINT FK_tb_dashboard_indicators_cod_qp FOREIGN KEY (cod_qp) REFERENCES enaplic_management.dbo.tb_status_qps(cod_qp);

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
DROP COLUMN des_qp

ALTER TABLE enaplic_management.dbo.tb_status_qps
ADD des_qp varchar(200) NOT NULL

CREATE TABLE tb_status_qps (
	id int IDENTITY(1,1) NOT NULL,
	cod_qp VARCHAR(6) NOT NULL PRIMARY KEY,
	des_qp varchar(200) NOT NULL,
	dt_open_qp varchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	dt_end_qp varchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	status_proj varchar(1) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	S_T_A_M_P datetime DEFAULT switchoffset(sysdatetimeoffset(),'-03:00') NOT NULL
);

EXEC sp_rename 'tb_open_qps.open_qp', 'cod_qp', 'COLUMN';

-- DROP TABLE tb_status_qps;

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
DROP CONSTRAINT FK_tb_dashboard_indicators_cod_qp


CREATE TABLE tb_closed_qps (
	id int IDENTITY(1,1) NOT NULL,
	cod_qp VARCHAR(6) NOT NULL PRIMARY KEY
);

DELETE FROM enaplic_management.dbo.tb_dashboard_indicators;

DELETE FROM enaplic_management.dbo.tb_open_qps;

ALTER TABLE tb_dashboard_indicators
ADD STAMP ROWVERSION;

-- Adicionar a coluna dt_open_qp
ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators 
ADD dt_start_proj VARCHAR(10);

-- Adicionar a coluna dt_end_qp
ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators 
ADD dt_end_proj VARCHAR(10);

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
DROP COLUMN status_proj;

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
ALTER COLUMN dt_open_qp VARCHAR(10);

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
ALTER COLUMN dt_end_qp VARCHAR(10);

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
ADD status_proj VARCHAR(1);

EXEC sp_rename 'tb_dashboard_indicators.vl_total_mp_cost', 'vl_total_mp_pc_cost', 'COLUMN';

EXEC sp_rename 'tb_dashboard_indicators.vl_open_op', 'vl_all_op', 'COLUMN';

EXEC sp_rename 'tb_dashboard_indicators.STAMP', 'S_T_A_M_P', 'COLUMN';

-- Etapa 1: Identificar e remover a restrição ou valor padrão associado à coluna S_T_A_M_P
-- Note que o nome da constraint pode variar, ajustamos conforme o erro fornecido

ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
DROP CONSTRAINT DF__tb_dashbo__S_T_A__49C3F6B7;

-- Etapa 2: Remover a coluna S_T_A_M_P
ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
DROP COLUMN S_T_A_M_P;

-- Etapa 3: Adicionar a coluna S_T_A_M_P com o tipo datetime e valor padrão ajustado para o horário do Brasil (UTC-3)
ALTER TABLE enaplic_management.dbo.tb_dashboard_indicators
ADD S_T_A_M_P datetime NOT NULL DEFAULT (SWITCHOFFSET(SYSDATETIMEOFFSET(), '-03:00'));

SELECT 
	*
FROM 
	enaplic_management.dbo.tb_dashboard_indicators
ORDER BY 
	id DESC;

SELECT 
	*
FROM 
	enaplic_management.dbo.tb_current_dashboard_indicators
ORDER BY 
	id DESC;

SELECT 
	* 
FROM 
	enaplic_management.dbo.tb_qps tq 
ORDER BY 
	id DESC;

SELECT 
	cod_qp AS "Código", 
    des_qp AS "Descrição", 
    status_qp AS "Status"
FROM 
	enaplic_management.dbo.tb_qps
ORDER BY 
	cod_qp DESC;

SELECT 
	* 
FROM 
	enaplic_management.dbo.tb_qps
ORDER BY 
	id DESC;

SELECT TOP 1 vl_proj_pi
FROM enaplic_management.dbo.tb_dashboard_indicators
WHERE cod_qp = '005552'
ORDER BY id DESC;


/*
 * CORRESPONDÊNCIA COLUNAS X INDICADORES
 * 
	vl_proj_all_prod = BASELINE
	vl_proj_prod_cancel = DESCONSIDERAR
	vl_proj_modify_perc = % MUDANCA
	vl_proj_released = PROJETO LIBERADO
	vl_proj_finished = PRONTO
	vl_proj_adjusted = EM AJUSTE
	vl_proj_pi = PI
	vl_proj_mp = MP
	vl_all_op = OP ABERTA
	vl_pcp_perc = IND. PCP (vl_all_op/vl_proj_pi) ***
	vl_closed_op = OP FECHADA
	vl_product_perc = IND. PROD. (vl_closed_op/vl_all_op)
	vl_all_sc = SC ABERTA
	vl_all_pc = PEDIDO DE COMPRA
	vl_compras_perc = IND. COMPRA (vl_all_pc/vl_all_sc)
	vl_mat_received = MATERIAL RECEBIDO
	vl_mat_received_perc = IND. RECEB. (vl_mat_received/vl_all_pc)
*/


