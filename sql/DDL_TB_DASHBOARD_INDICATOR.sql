-- enaplic_management.dbo.tb_dashboard_indicators definition

-- Drop table

-- DROP TABLE enaplic_management.dbo.tb_dashboard_indicators;

CREATE TABLE enaplic_management.dbo.tb_dashboard_indicators (
	id_indicator bigint IDENTITY(1,1) NOT NULL,
	cod_qp varchar(6) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	des_qp varchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	vl_proj_all_prod int NOT NULL,
	vl_proj_prod_cancel int NOT NULL,
	vl_proj_modify_perc decimal(3,2) NOT NULL,
	vl_proj_released int NOT NULL,
	vl_proj_finished int NOT NULL,
	vl_proj_adjusted int NOT NULL,
	vl_proj_pi int NOT NULL,
	vl_proj_mp int NOT NULL,
	vl_open_op int NOT NULL,
	vl_pcp_perc decimal(3,2) NOT NULL,
	vl_closed_op int NOT NULL,
	vl_product_perc decimal(3,2) NOT NULL,
	vl_all_sc int NOT NULL,
	vl_all_pc int NOT NULL,
	vl_compras_perc decimal(3,2) NOT NULL,
	vl_mat_received int NOT NULL,
	vl_mat_received_perc decimal(3,2) NOT NULL,
	CONSTRAINT PK__tb_dashb__9B1B8371FCA80F83 PRIMARY KEY (cod_qp)
);

--CREATE DATABASE enaplic_management;

--DROP DATABASE enaplic_management;

--USE enaplic_management;

CREATE TABLE tb_dashboard_indicators (
	id_indicator BIGINT NOT NULL IDENTITY(1,1),
    cod_qp VARCHAR(6) NOT NULL PRIMARY KEY,
    des_qp VARCHAR(200) NOT NULL,
    vl_proj_all_prod INT NOT NULL,
    vl_proj_prod_cancel INT NOT NULL,
    vl_proj_modify_perc DECIMAL(3, 2) NOT NULL,
    vl_proj_released INT NOT NULL,
    vl_proj_finished INT NOT NULL,
    vl_proj_adjusted INT NOT NULL,
    vl_proj_pi INT NOT NULL,
    vl_proj_mp INT NOT NULL,
    vl_open_op INT NOT NULL,
    vl_pcp_perc DECIMAL(3, 2) NOT NULL,
    vl_closed_op INT NOT NULL,
    vl_product_perc DECIMAL(3, 2) NOT NULL,
    vl_all_sc INT NOT NULL,
    vl_all_pc INT NOT NULL,
    vl_compras_perc DECIMAL(3, 2) NOT NULL,
    vl_mat_received INT NOT NULL,
    vl_mat_received_perc DECIMAL(3, 2) NOT NULL
);