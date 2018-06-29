/*
SQLyog Community v13.0.1 (64 bit)
MySQL - 5.7.22-0ubuntu18.04.1 : Database - bumps_db
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`bumps_db` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `bumps_db`;

/*Table structure for table `t_bumps_jobs` */

DROP TABLE IF EXISTS `t_bumps_jobs`;

CREATE TABLE `t_bumps_jobs` (
  `token` varchar(20) NOT NULL,
  `job_id` int(11) NOT NULL,
  `params` varchar(1024) DEFAULT NULL,
  `in_file_content` blob,
  PRIMARY KEY (`token`,`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
