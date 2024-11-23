-- MySQL dump 10.13  Distrib 9.0.1, for macos14.7 (x86_64)
--
-- Host: localhost    Database: loan_system
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_logs`
--

DROP TABLE IF EXISTS `activity_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(50) NOT NULL,
  `details` varchar(255) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=324 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
INSERT INTO `activity_logs` VALUES (1,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:31'),(2,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:31'),(3,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:44'),(4,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:44'),(5,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:35:28'),(6,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:35:38'),(7,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:35:42'),(8,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(9,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(10,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(11,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(12,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(13,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(14,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(15,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(16,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(17,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(18,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(19,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(20,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(21,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(22,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(23,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(24,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(25,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(26,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(27,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(28,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(29,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(30,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(31,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(32,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(33,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(34,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(35,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(36,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(37,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:21'),(38,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(39,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(40,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(41,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(42,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(43,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(44,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(45,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(46,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(47,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(48,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(49,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(50,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(51,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(52,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(53,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(54,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(55,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(56,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(57,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(58,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:54'),(59,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:54'),(60,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(61,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(62,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(63,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(64,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(65,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(66,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(67,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(68,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(69,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(70,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(71,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(72,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(73,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(74,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(75,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(76,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(77,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(78,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:39:26'),(79,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:39:31'),(80,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:39:33'),(81,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:09'),(82,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:13'),(83,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:15'),(84,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:15'),(85,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:41:56'),(86,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:41:59'),(87,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:42:01'),(88,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:42:04'),(89,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:42:09'),(90,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:00'),(91,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:10'),(92,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:16'),(93,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:18'),(94,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:20'),(95,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:46:22'),(96,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:48:04'),(97,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:48:04'),(98,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:48:46'),(99,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:48:46'),(100,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:49:08'),(101,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:49:08'),(102,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:49:51'),(103,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:49:51'),(104,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:49:54'),(105,1,'access_system_settings','Accessed /admin/system-settings via POST','127.0.0.1','2024-11-23 10:50:37'),(106,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:50:37'),(107,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:50:37'),(108,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:52:14'),(109,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:52:14'),(110,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:52:20'),(111,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:52:20'),(112,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:52:25'),(113,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:52:25'),(114,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:52:31'),(115,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:53:50'),(116,1,'access_system_settings','Accessed /admin/system-settings via POST','127.0.0.1','2024-11-23 10:53:59'),(117,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:53:59'),(118,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:53:59'),(119,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:56:51'),(120,1,'access_system_settings','Accessed /admin/system-settings via POST','127.0.0.1','2024-11-23 10:57:00'),(121,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:57:00'),(122,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:09'),(123,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:09'),(124,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:14'),(125,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:14'),(126,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:20'),(127,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:20'),(128,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:24'),(129,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:24'),(130,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:01:14'),(131,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:01:14'),(132,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:01:25'),(133,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:01:25'),(134,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:01:36'),(135,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:01:36'),(136,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:09'),(137,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:09'),(138,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:13'),(139,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:13'),(140,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:17'),(141,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:17'),(142,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:45'),(143,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:45'),(144,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:05:06'),(145,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:05:08'),(146,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:05:08'),(147,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:05:23'),(148,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:05:23'),(149,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:06:19'),(150,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:06:21'),(151,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:06:21'),(152,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:09:37'),(153,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:09:37'),(154,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:09:38'),(155,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:09:38'),(156,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:11:11'),(157,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:11:11'),(158,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:12:47'),(159,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:12:47'),(160,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:12:53'),(161,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:12:53'),(162,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:13:13'),(163,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:13:13'),(164,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:14:15'),(165,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:14:16'),(166,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:14:21'),(167,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:14:21'),(168,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:14:57'),(169,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:14:57'),(170,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:16:12'),(171,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:16:12'),(172,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:19:48'),(173,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:19:48'),(174,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:24:27'),(175,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:24:27'),(176,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:24:32'),(177,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:24:32'),(178,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:03'),(179,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:03'),(180,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:25:06'),(181,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:10'),(182,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:10'),(183,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:23'),(184,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:23'),(185,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:25:27'),(186,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:29'),(187,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:29'),(188,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:29:20'),(189,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:29:20'),(190,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:34:26'),(191,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:34:26'),(192,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:40:47'),(193,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:40:47'),(194,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:41:36'),(195,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:41:36'),(196,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:43:17'),(197,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:43:17'),(198,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:44:39'),(199,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:44:39'),(200,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:54:14'),(201,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:54:14'),(202,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:55:07'),(203,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:55:07'),(204,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:56:25'),(205,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:56:25'),(206,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:57:39'),(207,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:57:39'),(208,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:58:32'),(209,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:58:32'),(210,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:00:57'),(211,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:00:57'),(212,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:02:26'),(213,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:02:26'),(214,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:04:12'),(215,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:04:12'),(216,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:05:27'),(217,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:05:27'),(218,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:08:01'),(219,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:08:01'),(220,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:09:41'),(221,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:09:41'),(222,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:10:28'),(223,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:10:28'),(224,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:13:19'),(225,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:13:19'),(226,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:23:14'),(227,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:23:14'),(228,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:32:11'),(229,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:32:11'),(230,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:45:41'),(231,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:45:41'),(232,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:48:07'),(233,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:48:07'),(234,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:48:25'),(235,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:48:25'),(236,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:48:45'),(237,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:48:45'),(238,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:58:16'),(239,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:58:16'),(240,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:58:20'),(241,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:58:20'),(242,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:04:43'),(243,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:04:43'),(244,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:10:30'),(245,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:10:30'),(246,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:11:08'),(247,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:11:08'),(248,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:14:39'),(249,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:14:39'),(250,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:16:15'),(251,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:16:15'),(252,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:17:36'),(253,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:17:37'),(254,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:20:13'),(255,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:20:13'),(256,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:35:04'),(257,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:35:04'),(258,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:37:37'),(259,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:37:37'),(260,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:39:09'),(261,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:39:09'),(262,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:40:54'),(263,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:40:54'),(264,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:44:38'),(265,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:44:38'),(266,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:45:13'),(267,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:45:13'),(268,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:47:36'),(269,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:47:36'),(270,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:49:31'),(271,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:49:31'),(272,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:51:02'),(273,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:51:02'),(274,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:54:19'),(275,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:54:19'),(276,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:59:33'),(277,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:59:33'),(278,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:59:35'),(279,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:59:35'),(280,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:00:31'),(281,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:00:31'),(282,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:01:10'),(283,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:01:10'),(284,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:01:50'),(285,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:01:50'),(286,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:04:52'),(287,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:04:52'),(288,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:05:24'),(289,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:05:24'),(290,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:12:35'),(291,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:12:35'),(292,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:15:57'),(293,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:15:57'),(294,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:18:00'),(295,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:18:00'),(296,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:18:19'),(297,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:18:19'),(298,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:20:54'),(299,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:20:54'),(300,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:20:59'),(301,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:20:59'),(302,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:25:18'),(303,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:25:18'),(304,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:27:37'),(305,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:27:37'),(306,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:27:55'),(307,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:27:55'),(308,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:30:54'),(309,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:30:54'),(310,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:34:40'),(311,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:34:40'),(312,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:34:52'),(313,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:34:52'),(314,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:36:58'),(315,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:36:58'),(316,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:41:22'),(317,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:41:22'),(318,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:57:53'),(319,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:57:53'),(320,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 15:01:20'),(321,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 15:01:20'),(322,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 15:03:30'),(323,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 15:03:30');
/*!40000 ALTER TABLE `activity_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('update_admin_role_name');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `branches`
--

DROP TABLE IF EXISTS `branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `branches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(20) NOT NULL,
  `address` varchar(200) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `branches_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `branches_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `branches`
--

LOCK TABLES `branches` WRITE;
/*!40000 ALTER TABLE `branches` DISABLE KEYS */;
INSERT INTO `branches` VALUES (1,'Main Branch','MAIN','Main Street, City','2024-11-23 13:29:10','2024-11-23 13:29:10',1,NULL,1);
/*!40000 ALTER TABLE `branches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `client_types`
--

DROP TABLE IF EXISTS `client_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `client_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_name` varchar(100) DEFAULT NULL,
  `client_code` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int NOT NULL,
  `updated_by` int NOT NULL,
  `effective_from` date DEFAULT NULL,
  `effective_to` date DEFAULT NULL,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`client_code`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `client_types_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `client_types_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client_types`
--

LOCK TABLES `client_types` WRITE;
/*!40000 ALTER TABLE `client_types` DISABLE KEYS */;
INSERT INTO `client_types` VALUES (1,'Individual Client','IND','2024-11-23 13:29:10','2024-11-23 11:16:49',1,1,'2024-01-01','2027-12-31',1),(2,'Limited Liability Company','LLP','2024-11-23 11:24:07','2024-11-23 11:24:25',1,1,'2024-01-01','2027-12-31',1);
/*!40000 ALTER TABLE `client_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_type_id` int NOT NULL,
  `form_data` json NOT NULL,
  `files` json DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int NOT NULL,
  `updated_by` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_clients_client_type_id` (`client_type_id`),
  KEY `ix_clients_status` (`status`),
  KEY `ix_clients_created_at` (`created_at`),
  CONSTRAINT `clients_ibfk_1` FOREIGN KEY (`client_type_id`) REFERENCES `client_types` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `clients_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `clients_ibfk_3` FOREIGN KEY (`updated_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_fields`
--

DROP TABLE IF EXISTS `form_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_fields` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_id` int NOT NULL,
  `field_name` varchar(100) NOT NULL,
  `field_label` varchar(100) NOT NULL,
  `field_placeholder` varchar(200) DEFAULT NULL,
  `field_type` varchar(50) NOT NULL,
  `validation_text` varchar(200) DEFAULT NULL,
  `is_required` tinyint(1) DEFAULT NULL,
  `field_order` int DEFAULT NULL,
  `options` json DEFAULT NULL,
  `validation_rules` json DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `client_type_restrictions` json DEFAULT NULL COMMENT 'List of client type IDs that can see this field',
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `form_fields_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_fields`
--

LOCK TABLES `form_fields` WRITE;
/*!40000 ALTER TABLE `form_fields` DISABLE KEYS */;
INSERT INTO `form_fields` VALUES (1,8,'client_type','Client Type','Choose Client Type','select','Please select a client type',1,1,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(2,8,'purpose_of_visit','Purpose of Visit','Loan Inquiry','text','Please enter purpose of visit',1,2,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(3,8,'purpose_description','Purpose Description',NULL,'textarea',NULL,0,3,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(4,8,'product','Product','Choose Product','select','Please select a product',1,4,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(5,8,'first_name','First Name',NULL,'text','Please enter first name',1,5,NULL,'{\"minLength\": 2}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(6,8,'middle_name','Middle Name',NULL,'text',NULL,0,6,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(7,8,'last_name','Last Name',NULL,'text','Please enter last name',1,7,NULL,'{\"minLength\": 2}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(8,8,'gender','Gender','','radio','Please select gender',1,8,'[{\"label\": \"Male\", \"value\": \"M\"}, {\"label\": \"Female\", \"value\": \"F\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 12:13:33',NULL),(9,8,'id_type','ID Type','Choose ID Type','select','Please select ID type',1,9,'[{\"label\": \"National ID\", \"value\": \"national_id\"}, {\"label\": \"Military ID\", \"value\": \"military_id\"}, {\"label\": \"Alien ID\", \"value\": \"alien_id\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 12:10:05',NULL),(10,8,'id_number','ID Number / Company Registration',NULL,'text','Please enter ID number',1,10,NULL,'{\"pattern\": \"^[A-Z0-9]+$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(11,8,'serial_number','Serial Number (for National ID)',NULL,'text',NULL,0,11,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(12,8,'company_name','Group / Company Name / JV Name',NULL,'text',NULL,0,12,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(13,8,'birth_date','Birth Date / Company Registration Date',NULL,'date',NULL,0,13,NULL,'{\"maxDate\": \"today\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(14,8,'member_count','Number of Members / Partners / Directors','Enter Number','number',NULL,0,14,NULL,'{\"min\": 1}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(15,8,'postal_address','Postal Address',NULL,'text','Please enter postal address',1,15,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(16,8,'postal_code','Postal Code',NULL,'text','Please enter postal code',1,16,NULL,'{\"pattern\": \"^[0-9]+$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(17,8,'postal_town','Postal Town','Choose Town','select','Please select postal town',1,17,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(18,8,'mobile_phone','Mobile Phone','254-###-######','tel','Please enter valid mobile number',1,18,NULL,'{\"pattern\": \"^254[0-9]{9}$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(19,8,'email','Email Address',NULL,'email',NULL,0,19,NULL,'{\"pattern\": \"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(20,8,'county','County','Choose County','select','Please select county',1,20,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(21,8,'sub_county','Sub-County','Choose SubCounty','select','Please select sub-county',1,21,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(22,8,'ward','Ward',NULL,'text',NULL,0,22,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(23,8,'village','Village',NULL,'text',NULL,0,23,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL),(24,8,'trade_center','Nearest Trade Center','','text','',0,24,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 15:08:24','[1, 2]'),(25,8,'KRA PIN','KRA PIN','','text','This field is required',1,25,NULL,NULL,'2024-11-23 15:09:22','2024-11-23 15:09:22','[1, 2]');
/*!40000 ALTER TABLE `form_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modules`
--

DROP TABLE IF EXISTS `modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) NOT NULL,
  `description` text,
  `parent_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `modules_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `modules` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modules`
--

LOCK TABLES `modules` WRITE;
/*!40000 ALTER TABLE `modules` DISABLE KEYS */;
INSERT INTO `modules` VALUES (7,'Client Management','CLM00','Parent module for all client management functions',NULL,1,'2024-11-23 14:32:17','2024-11-23 14:32:17'),(8,'Prospect Registration','CLM01','Register new prospects before they become clients',7,1,'2024-11-23 14:32:36','2024-11-23 14:32:36'),(9,'Client Registration','CLM02','Register new clients with full KYC details',7,1,'2024-11-23 14:32:36','2024-11-23 14:32:36');
/*!40000 ALTER TABLE `modules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(10) NOT NULL,
  `status` varchar(20) NOT NULL,
  `interest_rate` varchar(10) NOT NULL,
  `rate_method` varchar(20) DEFAULT NULL,
  `processing_fee` varchar(50) DEFAULT NULL,
  `maintenance_fee` varchar(50) DEFAULT NULL,
  `insurance_fee` varchar(20) DEFAULT NULL,
  `frequency` varchar(10) DEFAULT NULL,
  `min_amount` decimal(20,2) NOT NULL,
  `max_amount` decimal(20,2) NOT NULL,
  `min_term` int NOT NULL,
  `max_term` int NOT NULL,
  `collateral` text,
  `income_statement` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `code` varchar(20) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `name` (`name`),
  KEY `fk_roles_created_by` (`created_by`),
  KEY `fk_roles_updated_by` (`updated_by`),
  CONSTRAINT `fk_roles_created_by` FOREIGN KEY (`created_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_roles_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `staff` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin','ADMIN','System Administrator','2024-11-23 13:29:10','2024-11-23 13:34:57',NULL,NULL,1),(2,'Branch Manager','BRANCH_MANAGER','Branch Manager','2024-11-23 13:29:10','2024-11-23 13:29:10',NULL,NULL,1),(3,'Loan Officer','LOAN_OFFICER','Loan Officer','2024-11-23 13:29:10','2024-11-23 13:29:10',NULL,NULL,1);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff`
--

DROP TABLE IF EXISTS `staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role_id` int NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `approved_by_id` int DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `branch_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  KEY `approved_by_id` (`approved_by_id`),
  KEY `ix_staff_status` (`status`),
  KEY `ix_staff_role_id` (`role_id`),
  KEY `ix_staff_branch_id` (`branch_id`),
  CONSTRAINT `fk_staff_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `staff_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `staff_ibfk_2` FOREIGN KEY (`approved_by_id`) REFERENCES `staff` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff`
--

LOCK TABLES `staff` WRITE;
/*!40000 ALTER TABLE `staff` DISABLE KEYS */;
INSERT INTO `staff` VALUES (1,'admin','admin@example.com','System','Administrator',NULL,'pbkdf2:sha256:600000$YOW4Dl2Jgej9O4z0$595a8b0c04431cd196ded1db15621ed65557ae4957794aeb404f3af978a20f98',1,'active',1,'2024-11-23 13:29:10','2024-11-23 13:29:10',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text,
  `setting_type` varchar(20) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`),
  UNIQUE KEY `idx_setting_key` (`setting_key`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `system_settings_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `staff` (`id`),
  CONSTRAINT `system_settings_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
INSERT INTO `system_settings` VALUES (1,'site_name','Loan Origination & Appraisal System','string','general','Site name displayed in the header','2024-11-23 10:53:17',1,'2024-11-23 10:53:17',NULL),(2,'site_description','',NULL,NULL,NULL,'2024-11-23 10:57:00',1,NULL,NULL),(3,'theme_mode','light',NULL,NULL,NULL,'2024-11-23 10:57:00',1,NULL,NULL),(4,'primary_color','#3B82F6',NULL,NULL,NULL,'2024-11-23 10:57:00',1,NULL,NULL),(5,'secondary_color','#1E40AF',NULL,NULL,NULL,'2024-11-23 10:57:00',1,NULL,NULL),(6,'site_logo','uploads/logos/Amica-Savings-Credit-tender.jpg',NULL,NULL,NULL,'2024-11-23 10:57:00',1,NULL,NULL);
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-23 18:12:27
