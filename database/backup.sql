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
) ENGINE=InnoDB AUTO_INCREMENT=614 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
INSERT INTO `activity_logs` VALUES (1,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:31'),(2,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:31'),(3,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:44'),(4,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:33:44'),(5,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:35:28'),(6,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:35:38'),(7,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:35:42'),(8,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(9,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(10,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(11,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(12,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(13,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(14,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(15,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(16,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(17,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:16'),(18,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(19,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(20,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(21,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:17'),(22,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(23,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(24,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(25,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(26,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(27,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:18'),(28,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(29,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(30,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(31,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(32,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(33,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(34,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(35,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(36,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:20'),(37,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:21'),(38,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(39,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(40,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(41,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(42,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(43,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(44,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(45,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(46,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(47,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:26'),(48,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(49,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(50,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(51,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(52,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(53,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(54,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(55,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(56,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(57,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:34'),(58,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:54'),(59,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:54'),(60,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(61,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(62,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(63,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(64,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(65,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(66,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(67,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:37:55'),(68,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(69,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(70,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(71,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(72,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(73,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(74,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(75,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(76,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(77,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:38:25'),(78,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:39:26'),(79,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:39:31'),(80,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:39:33'),(81,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:09'),(82,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:13'),(83,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:15'),(84,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:40:15'),(85,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:41:56'),(86,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:41:59'),(87,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:42:01'),(88,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:42:04'),(89,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:42:09'),(90,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:00'),(91,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:10'),(92,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:16'),(93,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:18'),(94,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:43:20'),(95,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:46:22'),(96,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:48:04'),(97,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:48:04'),(98,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:48:46'),(99,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:48:46'),(100,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:49:08'),(101,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:49:08'),(102,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:49:51'),(103,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:49:51'),(104,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:49:54'),(105,1,'access_system_settings','Accessed /admin/system-settings via POST','127.0.0.1','2024-11-23 10:50:37'),(106,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:50:37'),(107,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:50:37'),(108,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:52:14'),(109,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:52:14'),(110,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:52:20'),(111,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:52:20'),(112,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:52:25'),(113,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:52:25'),(114,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:52:31'),(115,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:53:50'),(116,1,'access_system_settings','Accessed /admin/system-settings via POST','127.0.0.1','2024-11-23 10:53:59'),(117,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:53:59'),(118,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:53:59'),(119,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:56:51'),(120,1,'access_system_settings','Accessed /admin/system-settings via POST','127.0.0.1','2024-11-23 10:57:00'),(121,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 10:57:00'),(122,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:09'),(123,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:09'),(124,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:14'),(125,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:14'),(126,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:20'),(127,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:20'),(128,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 10:57:24'),(129,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 10:57:24'),(130,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:01:14'),(131,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:01:14'),(132,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:01:25'),(133,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:01:25'),(134,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:01:36'),(135,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:01:36'),(136,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:09'),(137,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:09'),(138,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:13'),(139,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:13'),(140,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:17'),(141,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:17'),(142,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:04:45'),(143,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:04:45'),(144,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:05:06'),(145,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:05:08'),(146,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:05:08'),(147,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:05:23'),(148,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:05:23'),(149,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:06:19'),(150,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:06:21'),(151,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:06:21'),(152,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:09:37'),(153,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:09:37'),(154,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:09:38'),(155,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:09:38'),(156,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:11:11'),(157,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:11:11'),(158,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:12:47'),(159,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:12:47'),(160,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:12:53'),(161,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:12:53'),(162,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:13:13'),(163,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:13:13'),(164,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:14:15'),(165,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:14:16'),(166,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:14:21'),(167,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:14:21'),(168,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:14:57'),(169,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:14:57'),(170,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:16:12'),(171,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:16:12'),(172,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:19:48'),(173,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:19:48'),(174,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:24:27'),(175,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:24:27'),(176,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:24:32'),(177,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:24:32'),(178,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:03'),(179,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:03'),(180,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:25:06'),(181,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:10'),(182,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:10'),(183,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:23'),(184,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:23'),(185,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-23 11:25:27'),(186,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:25:29'),(187,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:25:29'),(188,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:29:20'),(189,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:29:20'),(190,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:34:26'),(191,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:34:26'),(192,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:40:47'),(193,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:40:47'),(194,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:41:36'),(195,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:41:36'),(196,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:43:17'),(197,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:43:17'),(198,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:44:39'),(199,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:44:39'),(200,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:54:14'),(201,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:54:14'),(202,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:55:07'),(203,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:55:07'),(204,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:56:25'),(205,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:56:25'),(206,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:57:39'),(207,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:57:39'),(208,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 11:58:32'),(209,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 11:58:32'),(210,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:00:57'),(211,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:00:57'),(212,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:02:26'),(213,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:02:26'),(214,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:04:12'),(215,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:04:12'),(216,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:05:27'),(217,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:05:27'),(218,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:08:01'),(219,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:08:01'),(220,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:09:41'),(221,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:09:41'),(222,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:10:28'),(223,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:10:28'),(224,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:13:19'),(225,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:13:19'),(226,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:23:14'),(227,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:23:14'),(228,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:32:11'),(229,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:32:11'),(230,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:45:41'),(231,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:45:41'),(232,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:48:07'),(233,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:48:07'),(234,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:48:25'),(235,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:48:25'),(236,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:48:45'),(237,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:48:45'),(238,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:58:16'),(239,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:58:16'),(240,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 12:58:20'),(241,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 12:58:20'),(242,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:04:43'),(243,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:04:43'),(244,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:10:30'),(245,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:10:30'),(246,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:11:08'),(247,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:11:08'),(248,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:14:39'),(249,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:14:39'),(250,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:16:15'),(251,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:16:15'),(252,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:17:36'),(253,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:17:37'),(254,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:20:13'),(255,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:20:13'),(256,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:35:04'),(257,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:35:04'),(258,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:37:37'),(259,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:37:37'),(260,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:39:09'),(261,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:39:09'),(262,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:40:54'),(263,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:40:54'),(264,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:44:38'),(265,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:44:38'),(266,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:45:13'),(267,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:45:13'),(268,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:47:36'),(269,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:47:36'),(270,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:49:31'),(271,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:49:31'),(272,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:51:02'),(273,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:51:02'),(274,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:54:19'),(275,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:54:19'),(276,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:59:33'),(277,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:59:33'),(278,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 13:59:35'),(279,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 13:59:35'),(280,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:00:31'),(281,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:00:31'),(282,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:01:10'),(283,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:01:10'),(284,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:01:50'),(285,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:01:50'),(286,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:04:52'),(287,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:04:52'),(288,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:05:24'),(289,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:05:24'),(290,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:12:35'),(291,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:12:35'),(292,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:15:57'),(293,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:15:57'),(294,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:18:00'),(295,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:18:00'),(296,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:18:19'),(297,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:18:19'),(298,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:20:54'),(299,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:20:54'),(300,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:20:59'),(301,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:20:59'),(302,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:25:18'),(303,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:25:18'),(304,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:27:37'),(305,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:27:37'),(306,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:27:55'),(307,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:27:55'),(308,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:30:54'),(309,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:30:54'),(310,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:34:40'),(311,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:34:40'),(312,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:34:52'),(313,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:34:52'),(314,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:36:58'),(315,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:36:58'),(316,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:41:22'),(317,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:41:22'),(318,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 14:57:53'),(319,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 14:57:53'),(320,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 15:01:20'),(321,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 15:01:20'),(322,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 15:03:30'),(323,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 15:03:30'),(324,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 15:13:53'),(325,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 15:13:53'),(326,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:34:52'),(327,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:34:52'),(328,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:35:30'),(329,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:35:30'),(330,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:35:54'),(331,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:35:54'),(332,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:48:51'),(333,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:48:51'),(334,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:49:53'),(335,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:49:53'),(336,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:53:35'),(337,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:53:35'),(338,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 19:57:36'),(339,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 19:57:36'),(340,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 20:12:14'),(341,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 20:12:14'),(342,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 20:22:28'),(343,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 20:22:28'),(344,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:06:27'),(345,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:06:27'),(346,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:10:53'),(347,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:10:53'),(348,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:10:55'),(349,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:10:55'),(350,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:16:59'),(351,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:16:59'),(352,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:18:38'),(353,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:18:38'),(354,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:18:59'),(355,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:18:59'),(356,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:23:16'),(357,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:23:16'),(358,1,'logout','User logged out','127.0.0.1','2024-11-23 21:23:20'),(359,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:23:45'),(360,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:23:45'),(361,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:23:47'),(362,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:23:47'),(363,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:41:16'),(364,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:41:16'),(365,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 21:44:44'),(366,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 21:44:44'),(367,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:27:29'),(368,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:27:29'),(369,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:31:33'),(370,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:31:33'),(371,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:32:27'),(372,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:32:27'),(373,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:35:33'),(374,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:35:33'),(375,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:39:14'),(376,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:39:14'),(377,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:41:29'),(378,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:41:29'),(379,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 22:41:56'),(380,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 22:41:56'),(381,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:01:04'),(382,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:01:04'),(383,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:07:51'),(384,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:07:52'),(385,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:07:57'),(386,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:07:57'),(387,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:08:02'),(388,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:08:02'),(389,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:08:16'),(390,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:08:16'),(391,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:08:22'),(392,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:08:22'),(393,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:20:56'),(394,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:20:56'),(395,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:23:32'),(396,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:23:32'),(397,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:37:36'),(398,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:37:36'),(399,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:44:14'),(400,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:44:15'),(401,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:51:06'),(402,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:51:06'),(403,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:56:55'),(404,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:56:55'),(405,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:57:28'),(406,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:57:29'),(407,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:57:40'),(408,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:57:40'),(409,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-23 23:59:04'),(410,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-23 23:59:04'),(411,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:30:15'),(412,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:30:15'),(413,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:30:21'),(414,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:30:28'),(415,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:30:28'),(416,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:30:55'),(417,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:30:55'),(418,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:30:58'),(419,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:33:31'),(420,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:33:31'),(421,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:33:37'),(422,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:33:37'),(423,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:33:40'),(424,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:33:42'),(425,1,'access_add_form_section','Accessed /admin/form-sections/add via POST','127.0.0.1','2024-11-24 13:33:59'),(426,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:33:59'),(427,1,'access_delete_form_section','Accessed /admin/form-sections/delete/1 via POST','127.0.0.1','2024-11-24 13:34:05'),(428,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:34:06'),(429,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:34:15'),(430,1,'access_add_form_section','Accessed /admin/form-sections/add via POST','127.0.0.1','2024-11-24 13:34:26'),(431,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:34:26'),(432,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:39:00'),(433,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:39:00'),(434,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:39:02'),(435,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:39:11'),(436,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:41:50'),(437,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:41:50'),(438,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:41:52'),(439,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:41:55'),(440,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:46:00'),(441,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:46:00'),(442,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:46:04'),(443,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:46:06'),(444,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:48:35'),(445,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:48:35'),(446,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:48:37'),(447,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:48:39'),(448,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:52:00'),(449,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:52:00'),(450,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:52:08'),(451,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:52:10'),(452,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 13:55:09'),(453,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 13:55:09'),(454,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:55:11'),(455,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:55:13'),(456,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:57:03'),(457,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:57:21'),(458,1,'access_delete_form_section','Accessed /admin/form-sections/delete/2 via POST','127.0.0.1','2024-11-24 13:57:26'),(459,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:57:26'),(460,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:57:28'),(461,1,'access_add_form_section','Accessed /admin/form-sections/add via POST','127.0.0.1','2024-11-24 13:57:39'),(462,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 13:59:08'),(463,1,'access_add_form_section','Accessed /admin/form-sections/add via POST','127.0.0.1','2024-11-24 13:59:20'),(464,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 13:59:20'),(465,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:06:46'),(466,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:06:46'),(467,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:06:49'),(468,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:06:52'),(469,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:09:02'),(470,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:09:32'),(471,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:09:32'),(472,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:09:34'),(473,1,'access_edit_form_section','Accessed /admin/form-sections/edit/3 via GET','127.0.0.1','2024-11-24 14:09:36'),(474,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:14:43'),(475,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:14:43'),(476,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:14:46'),(477,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:14:48'),(478,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:17:20'),(479,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:17:21'),(480,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:17:23'),(481,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:17:24'),(482,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:18:58'),(483,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:18:58'),(484,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:19:00'),(485,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:19:02'),(486,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:22:38'),(487,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:22:38'),(488,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:22:41'),(489,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:22:43'),(490,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:25:29'),(491,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:25:29'),(492,1,'access_form_sections','Accessed /admin/form-sections via GET','127.0.0.1','2024-11-24 14:25:31'),(493,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:25:33'),(494,1,'access_add_form_section','Accessed /admin/form-sections/add via GET','127.0.0.1','2024-11-24 14:25:49'),(495,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:30:05'),(496,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:30:05'),(497,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:30:29'),(498,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:30:29'),(499,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:40:51'),(500,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:40:51'),(501,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:41:12'),(502,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:41:12'),(503,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:42:20'),(504,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:42:21'),(505,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:42:26'),(506,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:42:26'),(507,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:42:45'),(508,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:42:45'),(509,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:46:17'),(510,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:46:17'),(511,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:47:55'),(512,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:47:55'),(513,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:47:56'),(514,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:47:56'),(515,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:47:59'),(516,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:47:59'),(517,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:51:20'),(518,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:51:20'),(519,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:51:23'),(520,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:51:23'),(521,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:51:25'),(522,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:51:26'),(523,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:59:48'),(524,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:59:48'),(525,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:59:53'),(526,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:59:53'),(527,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 14:59:58'),(528,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 14:59:58'),(529,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:00:00'),(530,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:00:00'),(531,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:00:08'),(532,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:00:08'),(533,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:03:37'),(534,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:03:37'),(535,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-24 15:03:40'),(536,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:03:45'),(537,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:03:45'),(538,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:03:49'),(539,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:03:49'),(540,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:03:52'),(541,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:03:52'),(542,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:04:01'),(543,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:04:01'),(544,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:04:09'),(545,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:04:09'),(546,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:06:47'),(547,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:06:47'),(548,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:09:58'),(549,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:09:58'),(550,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:11:26'),(551,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:11:26'),(552,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:12:57'),(553,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:12:57'),(554,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:13:06'),(555,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:13:06'),(556,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:15:02'),(557,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:15:02'),(558,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-24 15:15:07'),(559,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:15:10'),(560,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:15:10'),(561,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:15:14'),(562,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:15:14'),(563,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:21:12'),(564,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:21:12'),(565,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:24:17'),(566,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:24:17'),(567,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:35:30'),(568,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:35:30'),(569,1,'access_system_settings','Accessed /admin/system-settings via GET','127.0.0.1','2024-11-24 15:35:32'),(570,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:35:34'),(571,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:35:34'),(572,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:35:52'),(573,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:35:52'),(574,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:56:07'),(575,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:56:07'),(576,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 15:57:09'),(577,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 15:57:09'),(578,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:04:28'),(579,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:04:28'),(580,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:05:57'),(581,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:05:57'),(582,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:09:36'),(583,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:09:36'),(584,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:17:59'),(585,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:17:59'),(586,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:25:39'),(587,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:25:39'),(588,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:38:14'),(589,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:38:14'),(590,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:39:35'),(591,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:39:35'),(592,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:40:41'),(593,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:40:41'),(594,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:40:57'),(595,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:40:57'),(596,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:41:49'),(597,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:41:49'),(598,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:46:56'),(599,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:46:56'),(600,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:48:44'),(601,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:48:44'),(602,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:52:42'),(603,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:52:42'),(604,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:54:26'),(605,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:54:26'),(606,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:57:13'),(607,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:57:13'),(608,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 16:59:45'),(609,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 16:59:45'),(610,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 17:01:27'),(611,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 17:01:27'),(612,1,'access_admin_dashboard','Accessed /admin/dashboard via GET','127.0.0.1','2024-11-24 17:13:21'),(613,1,'view_admin_dashboard','Viewed admin dashboard','127.0.0.1','2024-11-24 17:13:21');
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
-- Table structure for table `form_data_clm01`
--

DROP TABLE IF EXISTS `form_data_clm01`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_data_clm01` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `submission_date` datetime NOT NULL,
  `status` varchar(20) NOT NULL,
  `client_type_id` int DEFAULT NULL,
  `client_type` varchar(255) NOT NULL,
  `purpose_of_visit` varchar(255) NOT NULL,
  `purpose_description` varchar(1000) DEFAULT NULL,
  `product` varchar(255) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `middle_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) NOT NULL,
  `gender` varchar(255) NOT NULL,
  `id_type` varchar(255) NOT NULL,
  `id_number` varchar(255) NOT NULL,
  `serial_number` varchar(255) DEFAULT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `birth_date` datetime DEFAULT NULL,
  `member_count` float DEFAULT NULL,
  `postal_address` varchar(255) NOT NULL,
  `postal_code` varchar(255) NOT NULL,
  `postal_town` varchar(255) NOT NULL,
  `mobile_phone` varchar(20) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `county` varchar(255) NOT NULL,
  `sub_county` varchar(255) NOT NULL,
  `ward` varchar(255) DEFAULT NULL,
  `village` varchar(255) DEFAULT NULL,
  `trade_center` varchar(255) DEFAULT NULL,
  `kra_pin` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `client_type_id` (`client_type_id`),
  CONSTRAINT `form_data_clm01_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `form_data_clm01_ibfk_2` FOREIGN KEY (`client_type_id`) REFERENCES `client_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_data_clm01`
--

LOCK TABLES `form_data_clm01` WRITE;
/*!40000 ALTER TABLE `form_data_clm01` DISABLE KEYS */;
INSERT INTO `form_data_clm01` VALUES (1,1,'2024-11-24 02:05:49','Pending',1,'Individual Client','Loan Inquiry',NULL,'1','Martin',NULL,'Sheen','M','national_id','787987',NULL,NULL,NULL,NULL,'990022','00200','Mombasa','2548892398',NULL,'Kwale','Lunga Lunga',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `form_data_clm01` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_data_clm02`
--

DROP TABLE IF EXISTS `form_data_clm02`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_data_clm02` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `submission_date` datetime NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `client_type_id` int DEFAULT NULL,
  `client_type` varchar(255) DEFAULT NULL,
  `marital_status` varchar(255) NOT NULL,
  `spouse_name` varchar(255) DEFAULT NULL,
  `spouse_id_type` varchar(255) DEFAULT NULL,
  `spouse_id_number` varchar(255) DEFAULT NULL,
  `children_below_12` float DEFAULT NULL,
  `children_13_to_18` float DEFAULT NULL,
  `children_above_18` float DEFAULT NULL,
  `dependants` float DEFAULT NULL,
  `nok_first_name` varchar(255) NOT NULL,
  `nok_middle_name` varchar(255) DEFAULT NULL,
  `nok_last_name` varchar(255) NOT NULL,
  `nok_id_type` varchar(255) NOT NULL,
  `nok_id_number` varchar(255) NOT NULL,
  `nok_postal_address` varchar(255) NOT NULL,
  `nok_postal_code` varchar(255) NOT NULL,
  `nok_postal_town` varchar(255) DEFAULT NULL,
  `nok_mobile_phone` varchar(20) NOT NULL,
  `occupation` varchar(255) NOT NULL,
  `occupation_type` varchar(255) NOT NULL,
  `employer_name` varchar(255) DEFAULT NULL,
  `business_address` varchar(255) DEFAULT NULL,
  `business_phone` varchar(20) DEFAULT NULL,
  `business_email` varchar(255) DEFAULT NULL,
  `professional_membership` varchar(255) DEFAULT NULL,
  `club_membership` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `client_type_id` (`client_type_id`),
  CONSTRAINT `form_data_clm02_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `form_data_clm02_ibfk_2` FOREIGN KEY (`client_type_id`) REFERENCES `client_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_data_clm02`
--

LOCK TABLES `form_data_clm02` WRITE;
/*!40000 ALTER TABLE `form_data_clm02` DISABLE KEYS */;
/*!40000 ALTER TABLE `form_data_clm02` ENABLE KEYS */;
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
  `section_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  KEY `fk_form_fields_section` (`section_id`),
  CONSTRAINT `fk_form_fields_section` FOREIGN KEY (`section_id`) REFERENCES `form_sections` (`id`) ON DELETE CASCADE,
  CONSTRAINT `form_fields_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_fields`
--

LOCK TABLES `form_fields` WRITE;
/*!40000 ALTER TABLE `form_fields` DISABLE KEYS */;
INSERT INTO `form_fields` VALUES (1,8,'client_type','Client Type','Choose Client Type','select','Please select a client type',1,1,'[{\"label\": \"Individual Client\", \"value\": \"1\"}, {\"label\": \"Limited Liability Company\", \"value\": \"2\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(2,8,'purpose_of_visit','Purpose of Visit','Loan Inquiry','text','Please enter purpose of visit',1,2,NULL,NULL,'2024-11-23 14:38:57','2024-11-24 16:41:18','[]',5),(3,8,'purpose_description','Purpose Description','','textarea','',1,3,NULL,NULL,'2024-11-23 14:38:57','2024-11-24 17:13:40','[]',NULL),(4,8,'product','Product','Choose Product','select','Please select a product',1,4,'[{\"label\": \"Business Loan\", \"value\": \"1\"}, {\"label\": \"Personal Loan\", \"value\": \"2\"}, {\"label\": \"Agriculture Loan\", \"value\": \"3\"}, {\"label\": \"SME Loan\", \"value\": \"4\"}, {\"label\": \"Emergency Loan\", \"value\": \"5\"}, {\"label\": \"Education Loan\", \"value\": \"6\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 23:05:49',NULL,NULL),(5,8,'first_name','First Name','','text','Please enter first name',1,5,NULL,'{\"minLength\": 2}','2024-11-23 14:38:57','2024-11-24 16:43:10','[]',5),(6,8,'middle_name','Middle Name','','text','',0,6,NULL,NULL,'2024-11-23 14:38:57','2024-11-24 16:43:44','[]',5),(7,8,'last_name','Last Name','','text','Please enter last name',1,7,NULL,'{\"minLength\": 2}','2024-11-23 14:38:57','2024-11-24 16:50:16','[]',5),(8,8,'gender','Gender','','radio','Please select gender',1,8,'[{\"label\": \"Male\", \"value\": \"M\"}, {\"label\": \"Female\", \"value\": \"F\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 22:42:20','[]',NULL),(9,8,'id_type','ID Type','Choose ID Type','select','Please select ID type',1,9,'[{\"label\": \"National ID\", \"value\": \"national_id\"}, {\"label\": \"Military ID\", \"value\": \"military_id\"}, {\"label\": \"Alien ID\", \"value\": \"alien_id\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 12:10:05',NULL,NULL),(10,8,'id_number','ID Number / Company Registration',NULL,'text','Please enter ID number',1,10,NULL,'{\"pattern\": \"^[A-Z0-9]+$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(11,8,'serial_number','Serial Number (for National ID)',NULL,'text',NULL,0,11,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(12,8,'company_name','Group / Company Name / JV Name','','text','',0,12,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 19:49:26','[2]',NULL),(13,8,'birth_date','Birth Date / Company Registration Date',NULL,'date',NULL,0,13,NULL,'{\"maxDate\": \"today\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(14,8,'member_count','Number of Members / Partners / Directors','Enter Number','number','',0,14,NULL,'{\"min\": 1}','2024-11-23 14:38:57','2024-11-23 19:49:44','[2]',NULL),(15,8,'postal_address','Postal Address',NULL,'text','Please enter postal address',1,15,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(16,8,'postal_code','Postal Code',NULL,'text','Please enter postal code',1,16,NULL,'{\"pattern\": \"^[0-9]+$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(17,8,'postal_town','Postal Town','Choose Town','select','Please select postal town',1,17,'[{\"label\": \"Mombasa\", \"value\": \"Mombasa\"}, {\"label\": \"Kwale\", \"value\": \"Kwale\"}, {\"label\": \"Kilifi\", \"value\": \"Kilifi\"}, {\"label\": \"Tana River\", \"value\": \"Tana River\"}, {\"label\": \"Lamu\", \"value\": \"Lamu\"}, {\"label\": \"Taita Taveta\", \"value\": \"Taita Taveta\"}, {\"label\": \"Garissa\", \"value\": \"Garissa\"}, {\"label\": \"Wajir\", \"value\": \"Wajir\"}, {\"label\": \"Mandera\", \"value\": \"Mandera\"}, {\"label\": \"Marsabit\", \"value\": \"Marsabit\"}, {\"label\": \"Isiolo\", \"value\": \"Isiolo\"}, {\"label\": \"Meru\", \"value\": \"Meru\"}, {\"label\": \"Tharaka Nithi\", \"value\": \"Tharaka Nithi\"}, {\"label\": \"Embu\", \"value\": \"Embu\"}, {\"label\": \"Kitui\", \"value\": \"Kitui\"}, {\"label\": \"Machakos\", \"value\": \"Machakos\"}, {\"label\": \"Makueni\", \"value\": \"Makueni\"}, {\"label\": \"Nyandarua\", \"value\": \"Nyandarua\"}, {\"label\": \"Nyeri\", \"value\": \"Nyeri\"}, {\"label\": \"Kirinyaga\", \"value\": \"Kirinyaga\"}, {\"label\": \"Murang\'a\", \"value\": \"Murang\'a\"}, {\"label\": \"Kiambu\", \"value\": \"Kiambu\"}, {\"label\": \"Turkana\", \"value\": \"Turkana\"}, {\"label\": \"West Pokot\", \"value\": \"West Pokot\"}, {\"label\": \"Samburu\", \"value\": \"Samburu\"}, {\"label\": \"Trans Nzoia\", \"value\": \"Trans Nzoia\"}, {\"label\": \"Uasin Gishu\", \"value\": \"Uasin Gishu\"}, {\"label\": \"Elgeyo Marakwet\", \"value\": \"Elgeyo Marakwet\"}, {\"label\": \"Nandi\", \"value\": \"Nandi\"}, {\"label\": \"Baringo\", \"value\": \"Baringo\"}, {\"label\": \"Laikipia\", \"value\": \"Laikipia\"}, {\"label\": \"Nakuru\", \"value\": \"Nakuru\"}, {\"label\": \"Narok\", \"value\": \"Narok\"}, {\"label\": \"Kajiado\", \"value\": \"Kajiado\"}, {\"label\": \"Kericho\", \"value\": \"Kericho\"}, {\"label\": \"Bomet\", \"value\": \"Bomet\"}, {\"label\": \"Kakamega\", \"value\": \"Kakamega\"}, {\"label\": \"Vihiga\", \"value\": \"Vihiga\"}, {\"label\": \"Bungoma\", \"value\": \"Bungoma\"}, {\"label\": \"Busia\", \"value\": \"Busia\"}, {\"label\": \"Siaya\", \"value\": \"Siaya\"}, {\"label\": \"Kisumu\", \"value\": \"Kisumu\"}, {\"label\": \"Homa Bay\", \"value\": \"Homa Bay\"}, {\"label\": \"Migori\", \"value\": \"Migori\"}, {\"label\": \"Kisii\", \"value\": \"Kisii\"}, {\"label\": \"Nyamira\", \"value\": \"Nyamira\"}, {\"label\": \"Nairobi\", \"value\": \"Nairobi\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 23:05:49',NULL,NULL),(18,8,'mobile_phone','Mobile Phone','254-###-######','tel','Please enter valid mobile number',1,18,NULL,'{\"pattern\": \"^254[0-9]{9}$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(19,8,'email','Email Address',NULL,'email',NULL,0,19,NULL,'{\"pattern\": \"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$\"}','2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(20,8,'county','County','Choose County','select','Please select county',1,20,'[{\"label\": \"Mombasa\", \"value\": \"Mombasa\"}, {\"label\": \"Kwale\", \"value\": \"Kwale\"}, {\"label\": \"Kilifi\", \"value\": \"Kilifi\"}, {\"label\": \"Tana River\", \"value\": \"Tana River\"}, {\"label\": \"Lamu\", \"value\": \"Lamu\"}, {\"label\": \"Taita Taveta\", \"value\": \"Taita Taveta\"}, {\"label\": \"Garissa\", \"value\": \"Garissa\"}, {\"label\": \"Wajir\", \"value\": \"Wajir\"}, {\"label\": \"Mandera\", \"value\": \"Mandera\"}, {\"label\": \"Marsabit\", \"value\": \"Marsabit\"}, {\"label\": \"Isiolo\", \"value\": \"Isiolo\"}, {\"label\": \"Meru\", \"value\": \"Meru\"}, {\"label\": \"Tharaka Nithi\", \"value\": \"Tharaka Nithi\"}, {\"label\": \"Embu\", \"value\": \"Embu\"}, {\"label\": \"Kitui\", \"value\": \"Kitui\"}, {\"label\": \"Machakos\", \"value\": \"Machakos\"}, {\"label\": \"Makueni\", \"value\": \"Makueni\"}, {\"label\": \"Nyandarua\", \"value\": \"Nyandarua\"}, {\"label\": \"Nyeri\", \"value\": \"Nyeri\"}, {\"label\": \"Kirinyaga\", \"value\": \"Kirinyaga\"}, {\"label\": \"Murang\'a\", \"value\": \"Murang\'a\"}, {\"label\": \"Kiambu\", \"value\": \"Kiambu\"}, {\"label\": \"Turkana\", \"value\": \"Turkana\"}, {\"label\": \"West Pokot\", \"value\": \"West Pokot\"}, {\"label\": \"Samburu\", \"value\": \"Samburu\"}, {\"label\": \"Trans Nzoia\", \"value\": \"Trans Nzoia\"}, {\"label\": \"Uasin Gishu\", \"value\": \"Uasin Gishu\"}, {\"label\": \"Elgeyo Marakwet\", \"value\": \"Elgeyo Marakwet\"}, {\"label\": \"Nandi\", \"value\": \"Nandi\"}, {\"label\": \"Baringo\", \"value\": \"Baringo\"}, {\"label\": \"Laikipia\", \"value\": \"Laikipia\"}, {\"label\": \"Nakuru\", \"value\": \"Nakuru\"}, {\"label\": \"Narok\", \"value\": \"Narok\"}, {\"label\": \"Kajiado\", \"value\": \"Kajiado\"}, {\"label\": \"Kericho\", \"value\": \"Kericho\"}, {\"label\": \"Bomet\", \"value\": \"Bomet\"}, {\"label\": \"Kakamega\", \"value\": \"Kakamega\"}, {\"label\": \"Vihiga\", \"value\": \"Vihiga\"}, {\"label\": \"Bungoma\", \"value\": \"Bungoma\"}, {\"label\": \"Busia\", \"value\": \"Busia\"}, {\"label\": \"Siaya\", \"value\": \"Siaya\"}, {\"label\": \"Kisumu\", \"value\": \"Kisumu\"}, {\"label\": \"Homa Bay\", \"value\": \"Homa Bay\"}, {\"label\": \"Migori\", \"value\": \"Migori\"}, {\"label\": \"Kisii\", \"value\": \"Kisii\"}, {\"label\": \"Nyamira\", \"value\": \"Nyamira\"}, {\"label\": \"Nairobi\", \"value\": \"Nairobi\"}]',NULL,'2024-11-23 14:38:57','2024-11-23 23:05:49',NULL,NULL),(21,8,'sub_county','Sub-County','Choose SubCounty','select','Please select sub-county',1,21,'[]',NULL,'2024-11-23 14:38:57','2024-11-23 23:05:49',NULL,NULL),(22,8,'ward','Ward',NULL,'text',NULL,0,22,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(23,8,'village','Village',NULL,'text',NULL,0,23,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 14:38:57',NULL,NULL),(24,8,'trade_center','Nearest Trade Center','','text','',0,24,NULL,NULL,'2024-11-23 14:38:57','2024-11-23 15:14:07','[1]',NULL),(33,8,'kra_pin','KRA PIN','','text','',0,25,NULL,NULL,'2024-11-23 23:01:32','2024-11-23 23:01:32','[1]',NULL),(34,9,'marital_status','Marital Status','','select',NULL,1,2,'[{\"label\": \"Single\", \"value\": \"single\"}, {\"label\": \"Married\", \"value\": \"married\"}, {\"label\": \"Divorced\", \"value\": \"divorced\"}, {\"label\": \"Widowed\", \"value\": \"widowed\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(35,9,'spouse_name','Spouse Name','','text',NULL,0,3,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(36,9,'spouse_id_type','ID Type','','select',NULL,0,4,'[{\"label\": \"National ID\", \"value\": \"national_id\"}, {\"label\": \"Passport\", \"value\": \"passport\"}, {\"label\": \"Military ID\", \"value\": \"military_id\"}, {\"label\": \"Alien ID\", \"value\": \"alien_id\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(37,9,'spouse_id_number','ID Number / Passport','','text',NULL,0,5,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(38,9,'children_below_12','Children (Below 12 Yrs)','1','number',NULL,0,6,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(39,9,'children_13_to_18','Children (Between 13 to 18 Yrs)','1','number',NULL,0,7,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(40,9,'children_above_18','Children (Above 18 Yrs)','1','number',NULL,0,8,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(41,9,'dependants','Dependants','1','number',NULL,0,9,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(42,9,'nok_first_name','First Name','','text',NULL,1,10,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(43,9,'nok_middle_name','Middle Name','','text',NULL,0,11,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(44,9,'nok_last_name','Last Name','','text',NULL,1,12,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(45,9,'nok_id_type','ID Type','','select',NULL,1,13,'[{\"label\": \"National ID\", \"value\": \"national_id\"}, {\"label\": \"Passport\", \"value\": \"passport\"}, {\"label\": \"Military ID\", \"value\": \"military_id\"}, {\"label\": \"Alien ID\", \"value\": \"alien_id\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(46,9,'nok_id_number','ID Number / Passport','','text',NULL,1,14,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(47,9,'nok_postal_address','Postal Address','','text',NULL,1,15,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(48,9,'nok_postal_code','Postal Code','','text',NULL,1,16,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(49,9,'nok_postal_town','Postal Town','Choose Town','select',NULL,0,17,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(50,9,'nok_mobile_phone','Mobile Phone','254_________','tel',NULL,1,18,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(51,9,'occupation','Occupation','','select',NULL,1,19,'[{\"label\": \"Employed\", \"value\": \"employed\"}, {\"label\": \"Self Employed\", \"value\": \"self_employed\"}, {\"label\": \"Business Owner\", \"value\": \"business_owner\"}, {\"label\": \"Retired\", \"value\": \"retired\"}, {\"label\": \"Student\", \"value\": \"student\"}, {\"label\": \"Other\", \"value\": \"other\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(52,9,'occupation_type','Occupation Type','','select',NULL,1,20,'[{\"label\": \"Full Time\", \"value\": \"full_time\"}, {\"label\": \"Part Time\", \"value\": \"part_time\"}, {\"label\": \"Contract\", \"value\": \"contract\"}, {\"label\": \"Casual\", \"value\": \"casual\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(53,9,'employer_name','Name of Employer / Business','','text',NULL,0,21,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(54,9,'business_address','Address / Location','','text',NULL,0,22,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(55,9,'business_phone','Phone Number','','tel',NULL,0,23,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(56,9,'business_email','Email Address','','email',NULL,0,24,'null',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(57,9,'professional_membership','Professional Membership','','select',NULL,0,25,'[{\"label\": \"None\", \"value\": \"none\"}, {\"label\": \"Engineering\", \"value\": \"engineering\"}, {\"label\": \"Medical\", \"value\": \"medical\"}, {\"label\": \"Legal\", \"value\": \"legal\"}, {\"label\": \"Accounting\", \"value\": \"accounting\"}, {\"label\": \"Other\", \"value\": \"other\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL),(58,9,'club_membership','Club Membership','','select',NULL,0,26,'[{\"label\": \"None\", \"value\": \"none\"}, {\"label\": \"Sports Club\", \"value\": \"sports\"}, {\"label\": \"Social Club\", \"value\": \"social\"}, {\"label\": \"Professional Club\", \"value\": \"professional\"}, {\"label\": \"Other\", \"value\": \"other\"}]',NULL,'2024-11-23 23:42:57','2024-11-23 23:42:57',NULL,NULL);
/*!40000 ALTER TABLE `form_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_sections`
--

DROP TABLE IF EXISTS `form_sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_sections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text,
  `order` int NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `client_type_restrictions` json DEFAULT NULL,
  `product_restrictions` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `form_sections_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_sections`
--

LOCK TABLES `form_sections` WRITE;
/*!40000 ALTER TABLE `form_sections` DISABLE KEYS */;
INSERT INTO `form_sections` VALUES (5,8,'Main','Prospect Main Section',0,1,'2024-11-24 12:47:30','2024-11-24 12:47:30','null','null'),(6,9,'General Information','Enter Client General Information',0,1,'2024-11-24 12:48:54','2024-11-24 12:48:54','null','null'),(7,9,'Company Information','Enter Company Information',1,1,'2024-11-24 12:49:26','2024-11-24 13:04:45','\"[2]\"','null'),(8,9,'Family Information','Enter Family Information',2,1,'2024-11-24 12:50:05','2024-11-24 13:05:48','\"[1]\"','null'),(9,9,'Next of Kin','Enter Next of Kin',3,1,'2024-11-24 12:50:29','2024-11-24 13:05:48','\"[1]\"','null'),(10,9,'Occupation','Enter Occupation Information',4,1,'2024-11-24 12:51:21','2024-11-24 13:05:48','\"[1]\"','null');
/*!40000 ALTER TABLE `form_sections` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Business Loan','BL001','Active','15%',NULL,NULL,NULL,NULL,NULL,10000.00,1000000.00,1,12,NULL,NULL,'2024-11-23 19:38:13','2024-11-23 19:38:13'),(2,'Personal Loan','PL001','Active','18%','Reducing Balance','2%','1%','0.5%','Monthly',5000.00,500000.00,3,36,'Salary, Assets','Required','2024-11-23 19:40:03','2024-11-23 19:40:03'),(3,'Agriculture Loan','AG001','Active','12%','Flat Rate','1.5%','0.5%','1%','Seasonal',50000.00,2000000.00,6,24,'Land Title, Machinery','Required','2024-11-23 19:40:03','2024-11-23 19:40:03'),(4,'SME Loan','SM001','Active','16%','Reducing Balance','2.5%','1%','0.75%','Monthly',100000.00,5000000.00,12,60,'Business Assets, Guarantors','Required','2024-11-23 19:40:03','2024-11-23 19:40:03'),(5,'Emergency Loan','EM001','Active','20%','Flat Rate','3%','0%','0.5%','Monthly',1000.00,50000.00,1,6,'Salary','Optional','2024-11-23 19:40:03','2024-11-23 19:40:03'),(6,'Education Loan','ED001','Active','14%','Reducing Balance','1%','0.5%','0.5%','Semester',10000.00,1000000.00,12,48,'Parent/Guardian Guarantee','Required','2024-11-23 19:40:03','2024-11-23 19:40:03');
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

-- Dump completed on 2024-11-24 20:44:03
