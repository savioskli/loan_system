-- MySQL dump 10.13  Distrib 9.0.1, for macos14.7 (x86_64)
--
-- Host: localhost    Database: sacco_db
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
-- Table structure for table `api_configs`
--

DROP TABLE IF EXISTS `api_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `api_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `base_url` varchar(255) NOT NULL,
  `port` int NOT NULL,
  `auth_type` varchar(50) DEFAULT NULL,
  `auth_credentials` json DEFAULT NULL,
  `headers` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `api_configs`
--

LOCK TABLES `api_configs` WRITE;
/*!40000 ALTER TABLE `api_configs` DISABLE KEYS */;
/*!40000 ALTER TABLE `api_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ArrearsManagement`
--

DROP TABLE IF EXISTS `ArrearsManagement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ArrearsManagement` (
  `ArrearsID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `CurrentArrears` decimal(15,2) NOT NULL,
  `ArrearsDays` int NOT NULL,
  `AgingBucket` enum('30 Days','60 Days','90 Days','Over 120 Days') NOT NULL,
  `DefaultRiskLevel` enum('Low','Medium','High') NOT NULL,
  `TotalPenaltyAccrued` decimal(15,2) DEFAULT '0.00',
  `LastRepaymentAmount` decimal(15,2) DEFAULT NULL,
  `LastRepaymentDate` date DEFAULT NULL,
  `NextDueDate` date DEFAULT NULL,
  `LegalActionFlag` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`ArrearsID`),
  KEY `LoanID` (`LoanID`),
  CONSTRAINT `arrearsmanagement_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ArrearsManagement`
--

LOCK TABLES `ArrearsManagement` WRITE;
/*!40000 ALTER TABLE `ArrearsManagement` DISABLE KEYS */;
INSERT INTO `ArrearsManagement` VALUES (1,8,175000.00,60,'60 Days','High',6000.00,10000.00,'2024-01-20','2024-02-01',0),(2,10,225000.00,45,'30 Days','High',10000.00,25000.00,'2024-01-10','2024-02-01',0),(3,6,25000.00,15,'30 Days','Medium',1000.00,25000.00,'2024-01-25','2024-02-01',0),(4,7,8000.00,10,'30 Days','Low',500.00,3000.00,'2024-01-15','2024-02-01',0);
/*!40000 ALTER TABLE `ArrearsManagement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Branches`
--

DROP TABLE IF EXISTS `Branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Branches` (
  `BranchID` int NOT NULL AUTO_INCREMENT,
  `BranchCode` varchar(20) NOT NULL,
  `BranchName` varchar(100) NOT NULL,
  `Location` varchar(255) NOT NULL,
  `Address` text,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `ManagerID` int DEFAULT NULL,
  `OpeningDate` date NOT NULL,
  `Status` enum('Active','Inactive') DEFAULT 'Active',
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `LastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`BranchID`),
  UNIQUE KEY `BranchCode` (`BranchCode`),
  KEY `ManagerID` (`ManagerID`),
  CONSTRAINT `branches_ibfk_1` FOREIGN KEY (`ManagerID`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Branches`
--

LOCK TABLES `Branches` WRITE;
/*!40000 ALTER TABLE `Branches` DISABLE KEYS */;
INSERT INTO `Branches` VALUES (1,'HQ001','Nairobi Main Branch','Nairobi CBD','Kimathi Street, Progressive House 2nd Floor','+254-020-2222111','nairobi.main@sacco.co.ke',1,'2020-01-01','Active','2024-12-31 07:26:20','2024-12-31 07:26:59'),(2,'WST002','Westlands Branch','Westlands','The Mall, Westlands Road','+254-020-2222112','westlands@sacco.co.ke',5,'2020-03-15','Active','2024-12-31 07:26:20','2024-12-31 07:26:59'),(3,'THK003','Thika Branch','Thika','Thika Business Center, Uhuru Street','+254-020-2222113','thika@sacco.co.ke',7,'2020-06-01','Active','2024-12-31 07:26:20','2024-12-31 07:26:59'),(4,'KSM004','Kisumu Branch','Kisumu','Mega Plaza, Oginga Odinga Road','+254-020-2222114','kisumu@sacco.co.ke',9,'2021-01-15','Active','2024-12-31 07:26:20','2024-12-31 07:26:59'),(5,'MBS005','Mombasa Branch','Mombasa','TSS Towers, Nkrumah Road','+254-020-2222115','mombasa@sacco.co.ke',NULL,'2021-03-01','Active','2024-12-31 07:26:20','2024-12-31 07:26:20');
/*!40000 ALTER TABLE `Branches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Charges`
--

DROP TABLE IF EXISTS `Charges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Charges` (
  `ChargeID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `ChargeType` enum('Processing Fee','Insurance','Legal Fee') NOT NULL,
  `ChargeAmount` decimal(15,2) NOT NULL,
  `ChargeDate` date NOT NULL,
  `PaymentStatus` enum('Pending','Settled') DEFAULT 'Pending',
  PRIMARY KEY (`ChargeID`),
  KEY `LoanID` (`LoanID`),
  CONSTRAINT `charges_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Charges`
--

LOCK TABLES `Charges` WRITE;
/*!40000 ALTER TABLE `Charges` DISABLE KEYS */;
INSERT INTO `Charges` VALUES (1,8,'Processing Fee',24000.00,'2023-07-01','Settled'),(2,8,'Insurance',36000.00,'2023-07-01','Settled'),(3,8,'Legal Fee',12000.00,'2024-01-15','Pending'),(4,10,'Processing Fee',50000.00,'2023-08-01','Settled'),(5,10,'Insurance',75000.00,'2023-08-01','Settled'),(6,10,'Legal Fee',25000.00,'2024-01-15','Pending'),(7,6,'Processing Fee',15000.00,'2023-06-11','Settled'),(8,6,'Insurance',22500.00,'2023-06-11','Settled'),(9,19,'Processing Fee',56000.00,'2023-12-21','Settled'),(10,19,'Insurance',84000.00,'2023-12-21','Settled'),(11,16,'Processing Fee',17000.00,'2023-11-11','Settled'),(12,16,'Insurance',25500.00,'2023-11-11','Settled'),(13,11,'Processing Fee',12000.00,'2023-08-21','Settled'),(14,11,'Insurance',18000.00,'2023-08-21','Settled'),(15,13,'Processing Fee',1900.00,'2023-09-21','Settled'),(16,13,'Insurance',2850.00,'2023-09-21','Settled'),(17,15,'Processing Fee',5600.00,'2023-10-21','Settled'),(18,15,'Insurance',8400.00,'2023-10-21','Settled');
/*!40000 ALTER TABLE `Charges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Collateral`
--

DROP TABLE IF EXISTS `Collateral`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Collateral` (
  `CollateralID` int NOT NULL AUTO_INCREMENT,
  `LoanAppID` int NOT NULL,
  `CollateralType` enum('Land','Car','Equipment') NOT NULL,
  `EstimatedValue` decimal(15,2) NOT NULL,
  `Description` text,
  `Status` enum('Active','Released') DEFAULT 'Active',
  PRIMARY KEY (`CollateralID`),
  KEY `LoanAppID` (`LoanAppID`),
  CONSTRAINT `collateral_ibfk_1` FOREIGN KEY (`LoanAppID`) REFERENCES `LoanApplications` (`LoanAppID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Collateral`
--

LOCK TABLES `Collateral` WRITE;
/*!40000 ALTER TABLE `Collateral` DISABLE KEYS */;
INSERT INTO `Collateral` VALUES (1,8,'Land',2500000.00,'Commercial Property in Nairobi CBD','Active'),(2,10,'Car',4500000.00,'Toyota Land Cruiser 2020','Active'),(3,6,'Land',1500000.00,'Residential Property in Westlands','Active'),(4,19,'Land',5000000.00,'Commercial Property in Mombasa','Active'),(5,16,'Car',3500000.00,'Mercedes Benz E300 2021','Active'),(6,11,'Equipment',1200000.00,'Industrial Printing Equipment','Active'),(7,13,'Equipment',200000.00,'Industrial Equipment','Active'),(8,15,'Land',800000.00,'Residential Property in Kilimani','Active');
/*!40000 ALTER TABLE `Collateral` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `database_configs`
--

DROP TABLE IF EXISTS `database_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `database_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` int NOT NULL,
  `user` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `database` varchar(100) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `database_configs`
--

LOCK TABLES `database_configs` WRITE;
/*!40000 ALTER TABLE `database_configs` DISABLE KEYS */;
INSERT INTO `database_configs` VALUES (1,'default','localhost',3306,'root','gAAAAABnc7Gno2XzjFwz_exqwwksAOJ9gOx9LwN2ImsAR6ElIpwkXhPmFTH1ohBpKDEM-8x4T-4iL8X1UJ50cckPPBU43sgTtA==','sacco_db',1,'2024-12-31 08:56:07','2024-12-31 08:56:07');
/*!40000 ALTER TABLE `database_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Deposits`
--

DROP TABLE IF EXISTS `Deposits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Deposits` (
  `DepositID` int NOT NULL AUTO_INCREMENT,
  `MemberID` int NOT NULL,
  `Amount` decimal(15,2) NOT NULL,
  `DepositDate` date NOT NULL,
  `DepositType` enum('Shares','Savings','Fixed') NOT NULL,
  `ReceivedBy` int NOT NULL,
  PRIMARY KEY (`DepositID`),
  KEY `MemberID` (`MemberID`),
  KEY `ReceivedBy` (`ReceivedBy`),
  CONSTRAINT `deposits_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`),
  CONSTRAINT `deposits_ibfk_2` FOREIGN KEY (`ReceivedBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Deposits`
--

LOCK TABLES `Deposits` WRITE;
/*!40000 ALTER TABLE `Deposits` DISABLE KEYS */;
INSERT INTO `Deposits` VALUES (1,1,50000.00,'2023-12-01','Savings',3),(2,2,30000.00,'2023-12-05','Savings',6),(3,3,100000.00,'2023-12-10','Fixed',3),(4,4,25000.00,'2023-12-15','Savings',6),(5,5,75000.00,'2023-12-20','Fixed',3),(6,6,40000.00,'2023-12-25','Savings',6),(7,7,60000.00,'2024-01-01','Savings',3),(8,8,35000.00,'2024-01-05','Savings',6),(9,9,80000.00,'2024-01-10','Fixed',3),(10,10,45000.00,'2024-01-15','Savings',6),(11,1,20000.00,'2024-01-15','Shares',3),(12,2,15000.00,'2024-01-15','Shares',6),(13,3,30000.00,'2024-01-15','Shares',3),(14,4,10000.00,'2024-01-15','Shares',6),(15,5,25000.00,'2024-01-15','Shares',3);
/*!40000 ALTER TABLE `Deposits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `GuarantorCommunications`
--

DROP TABLE IF EXISTS `GuarantorCommunications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GuarantorCommunications` (
  `CommunicationID` int NOT NULL AUTO_INCREMENT,
  `GuarantorID` int NOT NULL,
  `Type` enum('sms','email','call','letter','visit') NOT NULL,
  `Message` text NOT NULL,
  `Status` enum('pending','delivered','failed') NOT NULL DEFAULT 'pending',
  `Recipient` varchar(255) DEFAULT NULL,
  `CallDuration` int DEFAULT NULL,
  `CallOutcome` enum('successful','no_answer','voicemail','wrong_number') DEFAULT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `VisitPurpose` varchar(255) DEFAULT NULL,
  `VisitOutcome` enum('successful','not_available','rescheduled','cancelled') DEFAULT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` int NOT NULL,
  PRIMARY KEY (`CommunicationID`),
  KEY `GuarantorID` (`GuarantorID`),
  KEY `CreatedBy` (`CreatedBy`),
  CONSTRAINT `guarantorcommunications_ibfk_1` FOREIGN KEY (`GuarantorID`) REFERENCES `Guarantors` (`GuarantorID`),
  CONSTRAINT `guarantorcommunications_ibfk_2` FOREIGN KEY (`CreatedBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `GuarantorCommunications`
--

LOCK TABLES `GuarantorCommunications` WRITE;
/*!40000 ALTER TABLE `GuarantorCommunications` DISABLE KEYS */;
INSERT INTO `GuarantorCommunications` VALUES (1,1,'sms','Dear Elizabeth Njeri, This is a reminder that you are a guarantor for Loan No. L001/2023. Please ensure the borrower maintains timely repayments.','delivered','+254722111223',NULL,NULL,NULL,NULL,NULL,'2025-01-14 07:30:00',1),(2,2,'email','Dear Joseph Omondi, As a guarantor for Loan No. L001/2023, we would like to inform you that the next loan repayment is due on January 20th, 2025. Please ensure the borrower is aware of this deadline.','delivered','joseph@email.com',NULL,NULL,NULL,NULL,NULL,'2025-01-14 08:15:00',1),(3,3,'call','Called to discuss the loan repayment status and guarantor responsibilities for Loan No. L002/2023','delivered',NULL,15,'successful',NULL,NULL,NULL,'2025-01-14 09:00:00',1),(4,4,'letter','Formal notice regarding your guarantor obligations for Loan No. L003/2023. Please review the attached terms and conditions.','pending',NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-14 10:45:00',1),(5,5,'sms','Dear Michael Kiprop, Thank you for being a guarantor for Loan No. L003/2023. The loan is being serviced well, and we appreciate your support.','delivered','+254722111226',NULL,NULL,NULL,NULL,NULL,'2025-01-14 11:20:00',1);
/*!40000 ALTER TABLE `GuarantorCommunications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Guarantors`
--

DROP TABLE IF EXISTS `Guarantors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Guarantors` (
  `GuarantorID` int NOT NULL AUTO_INCREMENT,
  `LoanAppID` int NOT NULL,
  `GuarantorMemberID` int NOT NULL,
  `GuaranteedAmount` decimal(15,2) NOT NULL,
  `DateAdded` date NOT NULL,
  `Status` enum('Active','Released') DEFAULT 'Active',
  PRIMARY KEY (`GuarantorID`),
  KEY `LoanAppID` (`LoanAppID`),
  KEY `GuarantorMemberID` (`GuarantorMemberID`),
  CONSTRAINT `guarantors_ibfk_1` FOREIGN KEY (`LoanAppID`) REFERENCES `LoanApplications` (`LoanAppID`),
  CONSTRAINT `guarantors_ibfk_2` FOREIGN KEY (`GuarantorMemberID`) REFERENCES `Members` (`MemberID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Guarantors`
--

LOCK TABLES `Guarantors` WRITE;
/*!40000 ALTER TABLE `Guarantors` DISABLE KEYS */;
INSERT INTO `Guarantors` VALUES (1,1,2,250000.00,'2023-01-20','Active'),(2,1,3,250000.00,'2023-01-20','Active'),(3,2,1,80000.00,'2023-02-05','Active'),(4,3,4,750000.00,'2023-03-15','Active'),(5,3,5,750000.00,'2023-03-15','Active'),(6,5,1,1500000.00,'2023-05-05','Active'),(7,5,2,1500000.00,'2023-05-05','Active');
/*!40000 ALTER TABLE `Guarantors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanApplications`
--

DROP TABLE IF EXISTS `LoanApplications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanApplications` (
  `LoanAppID` int NOT NULL AUTO_INCREMENT,
  `LoanNo` varchar(50) NOT NULL,
  `MemberID` int NOT NULL,
  `ProductID` int NOT NULL,
  `ApplicationDate` date NOT NULL,
  `LoanAmount` decimal(15,2) NOT NULL,
  `RepaymentPeriod` int NOT NULL,
  `InterestRate` decimal(5,2) NOT NULL,
  `Purpose` text,
  `ApplicationStatus` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `AppraisedBy` int DEFAULT NULL,
  `AppraisalDate` date DEFAULT NULL,
  `ApprovalBy` int DEFAULT NULL,
  `ApprovalDate` date DEFAULT NULL,
  `Notes` text,
  `BranchID` int DEFAULT NULL,
  PRIMARY KEY (`LoanAppID`),
  UNIQUE KEY `LoanNo` (`LoanNo`),
  KEY `MemberID` (`MemberID`),
  KEY `AppraisedBy` (`AppraisedBy`),
  KEY `ApprovalBy` (`ApprovalBy`),
  KEY `fk_product` (`ProductID`),
  KEY `BranchID` (`BranchID`),
  CONSTRAINT `fk_product` FOREIGN KEY (`ProductID`) REFERENCES `LoanProducts` (`ProductID`),
  CONSTRAINT `loanapplications_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`),
  CONSTRAINT `loanapplications_ibfk_2` FOREIGN KEY (`AppraisedBy`) REFERENCES `Users` (`UserID`),
  CONSTRAINT `loanapplications_ibfk_3` FOREIGN KEY (`ApprovalBy`) REFERENCES `Users` (`UserID`),
  CONSTRAINT `loanapplications_ibfk_4` FOREIGN KEY (`BranchID`) REFERENCES `Branches` (`BranchID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanApplications`
--

LOCK TABLES `LoanApplications` WRITE;
/*!40000 ALTER TABLE `LoanApplications` DISABLE KEYS */;
INSERT INTO `LoanApplications` VALUES (1,'L001/2023',1,1,'2023-01-15',500000.00,24,14.00,'House Construction','Approved',4,'2023-01-20',1,'2023-01-25','All documents verified',1),(2,'L002/2023',2,2,'2023-02-01',80000.00,12,16.00,'Medical Emergency','Approved',4,'2023-02-05',1,'2023-02-07','Emergency loan approved',2),(3,'L003/2023',3,3,'2023-03-10',1500000.00,36,15.00,'Business Expansion','Approved',8,'2023-03-15',7,'2023-03-20','Business plan verified',3),(4,'L004/2023',4,4,'2023-04-01',200000.00,12,12.00,'School Fees','Pending',4,NULL,NULL,NULL,'Under review',4),(5,'L005/2023',5,5,'2023-05-01',3000000.00,48,13.50,'Equipment Purchase','Approved',8,'2023-05-05',7,'2023-05-10','Asset financing approved',5),(6,'L006/2023',6,1,'2023-06-01',750000.00,36,14.00,'Business Expansion','Approved',4,'2023-06-05',1,'2023-06-10','Business plan verified',1),(7,'L007/2023',7,2,'2023-06-15',90000.00,12,16.00,'Emergency Medical','Approved',4,'2023-06-18',1,'2023-06-20','Emergency approved',2),(8,'L008/2023',8,3,'2023-07-01',1200000.00,48,15.00,'Shop Expansion','Approved',8,'2023-07-05',7,'2023-07-10','Collateral verified',1),(9,'L009/2023',9,4,'2023-07-15',250000.00,12,12.00,'School Fees','Approved',4,'2023-07-18',1,'2023-07-20','School fees verified',4),(10,'L010/2023',10,5,'2023-08-01',2500000.00,60,13.50,'Equipment Purchase','Approved',8,'2023-08-05',7,'2023-08-10','Equipment quotation verified',5),(11,'L011/2023',11,1,'2023-08-15',600000.00,24,14.00,'Home Renovation','Approved',4,'2023-08-18',1,'2023-08-20','Renovation plan approved',2),(12,'L012/2023',12,3,'2023-09-01',1800000.00,48,15.00,'Business Startup','Pending',8,NULL,NULL,NULL,'Under review',3),(13,'L013/2023',13,2,'2023-09-15',95000.00,12,16.00,'Medical Emergency','Approved',4,'2023-09-18',1,'2023-09-20','Emergency approved',1),(14,'L014/2023',14,5,'2023-10-01',3500000.00,60,13.50,'Machinery Purchase','Rejected',8,'2023-10-05',7,'2023-10-10','Insufficient collateral',4),(15,'L015/2023',15,4,'2023-10-15',280000.00,12,12.00,'School Fees','Approved',4,'2023-10-18',1,'2023-10-20','School fees verified',5),(16,'L016/2023',16,1,'2023-11-01',850000.00,36,14.00,'Business Expansion','Approved',4,'2023-11-05',1,'2023-11-10','Business plan verified',2),(17,'L017/2023',17,3,'2023-11-15',1500000.00,48,15.00,'Shop Construction','Pending',8,NULL,NULL,NULL,'Awaiting documentation',3),(18,'L018/2023',18,2,'2023-12-01',85000.00,12,16.00,'Emergency','Approved',4,'2023-12-05',1,'2023-12-10','Emergency approved',4),(19,'L019/2023',19,5,'2023-12-15',2800000.00,60,13.50,'Vehicle Purchase','Approved',8,'2023-12-18',7,'2023-12-20','Vehicle valuation done',5),(20,'L020/2023',20,4,'2023-12-20',300000.00,12,12.00,'School Fees','Pending',4,NULL,NULL,NULL,'Awaiting school fee structure',1);
/*!40000 ALTER TABLE `LoanApplications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanCommunicationLog`
--

DROP TABLE IF EXISTS `LoanCommunicationLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanCommunicationLog` (
  `LogID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `MemberID` int NOT NULL,
  `CommunicationType` enum('SMS','Email','Letter','Phone Call') NOT NULL,
  `CommunicationPurpose` enum('Reminder','Default Notice','Collection','General') NOT NULL,
  `MessageContent` text,
  `SentDate` datetime NOT NULL,
  `SentBy` int NOT NULL,
  `DeliveryStatus` enum('Sent','Delivered','Failed') DEFAULT 'Sent',
  `ResponseReceived` text,
  `ResponseDate` datetime DEFAULT NULL,
  PRIMARY KEY (`LogID`),
  KEY `LoanID` (`LoanID`),
  KEY `MemberID` (`MemberID`),
  KEY `SentBy` (`SentBy`),
  CONSTRAINT `loancommunicationlog_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`),
  CONSTRAINT `loancommunicationlog_ibfk_2` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`),
  CONSTRAINT `loancommunicationlog_ibfk_3` FOREIGN KEY (`SentBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanCommunicationLog`
--

LOCK TABLES `LoanCommunicationLog` WRITE;
/*!40000 ALTER TABLE `LoanCommunicationLog` DISABLE KEYS */;
INSERT INTO `LoanCommunicationLog` VALUES (1,8,8,'SMS','Default Notice','Reminder: Your loan payment is overdue. Please make payment to avoid penalties.','2024-01-01 09:00:00',3,'Delivered',NULL,NULL),(2,8,8,'Email','Collection','Final reminder for overdue loan payment. Please contact our office immediately.','2024-01-05 10:30:00',3,'Delivered',NULL,NULL),(3,10,10,'SMS','Default Notice','Your loan payment is overdue. Please make payment to avoid additional penalties.','2024-01-01 09:15:00',6,'Delivered',NULL,NULL),(4,10,10,'Email','Collection','Notice: Your loan account requires immediate attention. Please contact us.','2024-01-10 11:00:00',6,'Delivered',NULL,NULL),(5,6,6,'SMS','Reminder','Reminder: Loan payment due today. Please process your payment.','2024-01-05 08:30:00',3,'Delivered',NULL,NULL),(6,7,7,'Email','Reminder','Your partial payment has been received. Please clear the remaining balance.','2024-01-02 14:00:00',6,'Delivered',NULL,NULL),(7,13,13,'SMS','General','Thank you for your advance loan payment.','2024-01-01 16:45:00',3,'Delivered',NULL,NULL),(8,19,19,'Email','General','Confirmation: Your loan payment has been received.','2024-01-01 17:00:00',3,'Delivered',NULL,NULL),(9,1,1,'Phone Call','Collection','Called to discuss overdue loan payment. Member promised to pay by end of week.','2025-01-04 10:30:00',2,'Delivered','Member will pay KES 25,000 by Friday','2025-01-04 10:35:00'),(10,2,2,'Email','Reminder','Your loan payment of KES 15,000 is due in 3 days. Please ensure timely payment.','2025-01-04 09:00:00',3,'Failed',NULL,NULL),(11,3,3,'SMS','Default Notice','URGENT: Your loan is 45 days overdue. Please contact us immediately to avoid legal action.','2025-01-04 08:15:00',1,'Delivered',NULL,NULL),(12,4,4,'Letter','Default Notice','Formal notice of loan default. Please schedule a meeting with our recovery team.','2025-01-03 14:20:00',2,'Sent',NULL,NULL),(13,5,5,'Phone Call','Collection','Discussed restructuring options for the overdue loan.','2025-01-03 11:45:00',4,'Delivered','Member requested loan restructuring form','2025-01-03 11:50:00'),(14,1,1,'SMS','Reminder','Reminder: Your promised payment of KES 25,000 is due tomorrow.','2025-01-03 16:00:00',2,'Delivered',NULL,NULL),(15,2,2,'Phone Call','General','Called to verify email address due to failed delivery.','2025-01-03 15:30:00',3,'Delivered','Member provided new email: elizabeth.n@gmail.com','2025-01-03 15:35:00'),(16,3,3,'Email','Collection','Payment plan proposal for your overdue loan.','2025-01-03 14:00:00',1,'Delivered','Accepted payment plan','2025-01-03 16:20:00'),(17,4,4,'SMS','Reminder','Your loan payment is due in 5 days. Current balance: KES 45,000','2025-01-02 09:00:00',5,'Delivered',NULL,NULL),(18,5,5,'Email','General','Loan restructuring forms attached as requested.','2025-01-02 12:30:00',4,'Delivered','Forms received, will submit by tomorrow','2025-01-02 14:15:00');
/*!40000 ALTER TABLE `LoanCommunicationLog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanDisbursements`
--

DROP TABLE IF EXISTS `LoanDisbursements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanDisbursements` (
  `DisbursementID` int NOT NULL AUTO_INCREMENT,
  `LoanAppID` int NOT NULL,
  `DisbursementAmount` decimal(15,2) NOT NULL,
  `DisbursementDate` date NOT NULL,
  `DisbursedBy` int NOT NULL,
  `RepaymentStartDate` date NOT NULL,
  `LoanStatus` enum('Active','Settled','Defaulted') DEFAULT 'Active',
  PRIMARY KEY (`DisbursementID`),
  KEY `LoanAppID` (`LoanAppID`),
  KEY `DisbursedBy` (`DisbursedBy`),
  CONSTRAINT `loandisbursements_ibfk_1` FOREIGN KEY (`LoanAppID`) REFERENCES `LoanApplications` (`LoanAppID`),
  CONSTRAINT `loandisbursements_ibfk_2` FOREIGN KEY (`DisbursedBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanDisbursements`
--

LOCK TABLES `LoanDisbursements` WRITE;
/*!40000 ALTER TABLE `LoanDisbursements` DISABLE KEYS */;
INSERT INTO `LoanDisbursements` VALUES (1,1,500000.00,'2023-01-26',3,'2023-02-01','Active'),(2,2,80000.00,'2023-02-08',6,'2023-03-01','Active'),(3,3,1500000.00,'2023-03-21',3,'2023-04-01','Active'),(4,5,3000000.00,'2023-05-11',6,'2023-06-01','Active'),(5,6,750000.00,'2023-06-11',3,'2023-07-01','Active'),(6,7,90000.00,'2023-06-21',6,'2023-07-01','Active'),(7,8,1200000.00,'2023-07-11',3,'2023-08-01','Defaulted'),(8,9,250000.00,'2023-07-21',6,'2023-08-01','Active'),(9,10,2500000.00,'2023-08-11',3,'2023-09-01','Defaulted'),(10,11,600000.00,'2023-08-21',6,'2023-09-01','Active'),(11,13,95000.00,'2023-09-21',3,'2023-10-01','Active'),(12,15,280000.00,'2023-10-21',6,'2023-11-01','Active'),(13,16,850000.00,'2023-11-11',3,'2023-12-01','Active'),(14,18,85000.00,'2023-12-11',6,'2024-01-01','Active'),(15,19,2800000.00,'2023-12-21',3,'2024-01-01','Active');
/*!40000 ALTER TABLE `LoanDisbursements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanHistory`
--

DROP TABLE IF EXISTS `LoanHistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanHistory` (
  `HistoryID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `MemberID` int NOT NULL,
  `ActionType` enum('Application','Appraisal','Approval','Disbursement','Repayment','Restructure','Close') NOT NULL,
  `ActionDate` datetime NOT NULL,
  `ActionBy` int NOT NULL,
  `PreviousStatus` varchar(50) DEFAULT NULL,
  `NewStatus` varchar(50) DEFAULT NULL,
  `Comments` text,
  `SystemNotes` text,
  PRIMARY KEY (`HistoryID`),
  KEY `LoanID` (`LoanID`),
  KEY `MemberID` (`MemberID`),
  KEY `ActionBy` (`ActionBy`),
  CONSTRAINT `loanhistory_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`),
  CONSTRAINT `loanhistory_ibfk_2` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`),
  CONSTRAINT `loanhistory_ibfk_3` FOREIGN KEY (`ActionBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanHistory`
--

LOCK TABLES `LoanHistory` WRITE;
/*!40000 ALTER TABLE `LoanHistory` DISABLE KEYS */;
INSERT INTO `LoanHistory` VALUES (1,8,8,'Application','2023-07-01 09:00:00',3,NULL,'Pending','New loan application received','Application created'),(2,8,8,'Appraisal','2023-07-05 14:00:00',4,'Pending','Under Review','Loan appraisal completed','Appraisal completed by loan officer'),(3,8,8,'Approval','2023-07-10 11:00:00',1,'Under Review','Approved','Loan approved by credit committee','Approval granted'),(4,8,8,'Disbursement','2023-07-11 15:00:00',3,'Approved','Active','Loan funds disbursed','Disbursement processed'),(5,8,8,'Repayment','2024-01-20 10:00:00',3,'Active','Defaulted','Partial payment received','Payment recorded but loan in default'),(6,10,10,'Application','2023-08-01 10:00:00',6,NULL,'Pending','New loan application received','Application created'),(7,10,10,'Appraisal','2023-08-05 11:00:00',4,'Pending','Under Review','Loan appraisal completed','Appraisal completed by loan officer'),(8,10,10,'Approval','2023-08-10 14:00:00',1,'Under Review','Approved','Loan approved by credit committee','Approval granted'),(9,10,10,'Disbursement','2023-08-11 16:00:00',3,'Approved','Active','Loan funds disbursed','Disbursement processed'),(10,10,10,'Repayment','2024-01-10 09:00:00',3,'Active','Defaulted','Partial payment received','Payment recorded but loan in default'),(11,6,6,'Application','2023-06-01 09:00:00',3,NULL,'Pending','New loan application received','Application created'),(12,6,6,'Approval','2023-06-10 15:00:00',1,'Under Review','Approved','Loan approved','Approval granted'),(13,6,6,'Disbursement','2023-06-11 10:00:00',3,'Approved','Active','Loan funds disbursed','Disbursement processed'),(14,6,6,'Repayment','2024-01-25 14:00:00',3,'Active','Active','Late payment received','Payment recorded'),(15,13,13,'Application','2023-09-15 11:00:00',3,NULL,'Pending','New loan application received','Application created'),(16,13,13,'Approval','2023-09-20 16:00:00',1,'Under Review','Approved','Loan approved','Approval granted'),(17,13,13,'Disbursement','2023-09-21 10:00:00',3,'Approved','Active','Loan funds disbursed','Disbursement processed'),(18,13,13,'Repayment','2024-01-01 09:00:00',3,'Active','Active','Regular payment received','Payment recorded');
/*!40000 ALTER TABLE `LoanHistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanLedgerEntries`
--

DROP TABLE IF EXISTS `LoanLedgerEntries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanLedgerEntries` (
  `LedgerID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `MemberID` int NOT NULL,
  `DisbursedAmount` decimal(15,2) NOT NULL,
  `OutstandingBalance` decimal(15,2) NOT NULL,
  `RepaymentDueDate` date NOT NULL,
  `ActualRepaymentDate` date DEFAULT NULL,
  `PenaltyAmount` decimal(15,2) DEFAULT '0.00',
  `ArrearsAmount` decimal(15,2) DEFAULT '0.00',
  `ArrearsDays` int DEFAULT '0',
  `InterestAccrued` decimal(15,2) DEFAULT '0.00',
  `TransactionType` enum('Repayment','Penalty','Interest Adjustment') NOT NULL,
  PRIMARY KEY (`LedgerID`),
  KEY `LoanID` (`LoanID`),
  KEY `MemberID` (`MemberID`),
  CONSTRAINT `loanledgerentries_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`),
  CONSTRAINT `loanledgerentries_ibfk_2` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanLedgerEntries`
--

LOCK TABLES `LoanLedgerEntries` WRITE;
/*!40000 ALTER TABLE `LoanLedgerEntries` DISABLE KEYS */;
INSERT INTO `LoanLedgerEntries` VALUES (1,8,8,1200000.00,1025000.00,'2024-01-01','2024-01-20',6000.00,175000.00,60,15000.00,'Repayment'),(2,8,8,1200000.00,1025000.00,'2024-01-01','2024-01-20',6000.00,175000.00,60,15000.00,'Penalty'),(3,10,10,2500000.00,2275000.00,'2024-01-01','2024-01-10',10000.00,225000.00,45,28000.00,'Repayment'),(4,10,10,2500000.00,2275000.00,'2024-01-01','2024-01-10',10000.00,225000.00,45,28000.00,'Penalty'),(5,6,6,750000.00,550000.00,'2024-01-01','2024-01-25',1000.00,25000.00,15,8000.00,'Repayment'),(6,6,6,750000.00,550000.00,'2024-01-01','2024-01-25',1000.00,25000.00,15,8000.00,'Penalty'),(7,7,7,90000.00,34000.00,'2024-01-01','2024-01-15',500.00,8000.00,10,1200.00,'Repayment'),(8,13,13,95000.00,49500.00,'2024-01-01','2024-01-01',0.00,0.00,0,1500.00,'Repayment'),(9,15,15,280000.00,208000.00,'2024-01-01','2024-01-01',0.00,0.00,0,3500.00,'Repayment'),(10,16,16,850000.00,798000.00,'2024-01-01','2024-01-01',0.00,0.00,0,10000.00,'Repayment'),(11,1,1,500000.00,350000.00,'2023-12-01',NULL,0.00,45000.00,35,12500.00,'Repayment'),(12,2,2,80000.00,45000.00,'2023-11-01',NULL,0.00,35000.00,65,4800.00,'Repayment'),(13,3,3,1500000.00,1200000.00,'2023-10-01',NULL,0.00,180000.00,95,45000.00,'Repayment'),(14,5,5,3000000.00,2500000.00,'2023-09-01',NULL,0.00,450000.00,125,90000.00,'Repayment'),(15,9,9,250000.00,180000.00,'2023-08-01',NULL,0.00,95000.00,155,7500.00,'Repayment'),(16,11,11,600000.00,450000.00,'2023-07-01',NULL,0.00,200000.00,185,18000.00,'Repayment'),(17,18,18,85000.00,75000.00,'2023-06-01',NULL,0.00,55000.00,215,2550.00,'Repayment'),(18,19,19,2800000.00,2500000.00,'2023-05-01',NULL,0.00,850000.00,365,84000.00,'Repayment');
/*!40000 ALTER TABLE `LoanLedgerEntries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanProducts`
--

DROP TABLE IF EXISTS `LoanProducts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanProducts` (
  `ProductID` int NOT NULL AUTO_INCREMENT,
  `ProductName` varchar(100) NOT NULL,
  `MinAmount` decimal(15,2) NOT NULL,
  `MaxAmount` decimal(15,2) NOT NULL,
  `DefaultInterestRate` decimal(5,2) NOT NULL,
  `DefaultRepaymentPeriod` int NOT NULL,
  `CollateralRequired` tinyint(1) DEFAULT '0',
  `GuarantorRequirement` tinyint(1) DEFAULT '0',
  `Status` enum('Active','Inactive') DEFAULT 'Active',
  PRIMARY KEY (`ProductID`),
  UNIQUE KEY `ProductName` (`ProductName`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanProducts`
--

LOCK TABLES `LoanProducts` WRITE;
/*!40000 ALTER TABLE `LoanProducts` DISABLE KEYS */;
INSERT INTO `LoanProducts` VALUES (1,'Development Loan',50000.00,1000000.00,14.00,36,1,1,'Active'),(2,'Emergency Loan',10000.00,100000.00,16.00,12,0,1,'Active'),(3,'Business Loan',100000.00,2000000.00,15.00,48,1,1,'Active'),(4,'School Fees Loan',20000.00,300000.00,12.00,12,0,1,'Active'),(5,'Asset Financing',200000.00,5000000.00,13.50,60,1,1,'Active');
/*!40000 ALTER TABLE `LoanProducts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanRepayments`
--

DROP TABLE IF EXISTS `LoanRepayments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanRepayments` (
  `RepaymentID` int NOT NULL AUTO_INCREMENT,
  `LoanAppID` int NOT NULL,
  `RepaymentAmount` decimal(15,2) NOT NULL,
  `RepaymentDate` date NOT NULL,
  `PaymentMethod` enum('Bank','Cash','Mobile Money') NOT NULL,
  `ReceivedBy` int NOT NULL,
  `BalanceRemaining` decimal(15,2) NOT NULL,
  PRIMARY KEY (`RepaymentID`),
  KEY `LoanAppID` (`LoanAppID`),
  KEY `ReceivedBy` (`ReceivedBy`),
  CONSTRAINT `loanrepayments_ibfk_1` FOREIGN KEY (`LoanAppID`) REFERENCES `LoanApplications` (`LoanAppID`),
  CONSTRAINT `loanrepayments_ibfk_2` FOREIGN KEY (`ReceivedBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanRepayments`
--

LOCK TABLES `LoanRepayments` WRITE;
/*!40000 ALTER TABLE `LoanRepayments` DISABLE KEYS */;
INSERT INTO `LoanRepayments` VALUES (1,1,25000.00,'2023-02-01','Bank',3,475000.00),(2,1,25000.00,'2023-03-01','Bank',3,450000.00),(3,2,8000.00,'2023-03-01','Mobile Money',6,72000.00),(4,2,8000.00,'2023-04-01','Mobile Money',6,64000.00),(5,3,50000.00,'2023-04-01','Bank',3,1450000.00),(6,3,50000.00,'2023-05-01','Bank',3,1400000.00),(7,6,25000.00,'2023-07-01','Bank',3,725000.00),(8,6,25000.00,'2023-08-01','Bank',3,700000.00),(9,6,25000.00,'2023-09-01','Bank',3,675000.00),(10,6,25000.00,'2023-10-01','Bank',3,650000.00),(11,6,25000.00,'2023-11-01','Bank',3,625000.00),(12,6,25000.00,'2023-12-01','Bank',3,600000.00),(13,7,8000.00,'2023-07-01','Mobile Money',6,82000.00),(14,7,8000.00,'2023-08-01','Mobile Money',6,74000.00),(15,7,8000.00,'2023-09-01','Mobile Money',6,66000.00),(16,7,8000.00,'2023-10-01','Mobile Money',6,58000.00),(17,7,8000.00,'2023-11-01','Mobile Money',6,50000.00),(18,7,8000.00,'2023-12-01','Mobile Money',6,42000.00),(19,8,30000.00,'2023-08-01','Bank',3,1170000.00),(20,8,30000.00,'2023-09-01','Bank',3,1140000.00),(21,8,30000.00,'2023-10-01','Bank',3,1110000.00),(22,8,30000.00,'2023-11-01','Bank',3,1080000.00),(23,8,30000.00,'2023-12-01','Bank',3,1050000.00),(24,9,22000.00,'2023-08-01','Mobile Money',6,228000.00),(25,9,22000.00,'2023-09-01','Mobile Money',6,206000.00),(26,9,22000.00,'2023-10-01','Mobile Money',6,184000.00),(27,9,22000.00,'2023-11-01','Mobile Money',6,162000.00),(28,9,22000.00,'2023-12-01','Mobile Money',6,140000.00),(29,10,50000.00,'2023-09-01','Bank',3,2450000.00),(30,10,50000.00,'2023-10-01','Bank',3,2400000.00),(31,10,50000.00,'2023-11-01','Bank',3,2350000.00),(32,10,50000.00,'2023-12-01','Bank',3,2300000.00),(33,11,28000.00,'2023-09-01','Bank',6,572000.00),(34,11,28000.00,'2023-10-01','Bank',6,544000.00),(35,11,28000.00,'2023-11-01','Bank',6,516000.00),(36,11,28000.00,'2023-12-01','Bank',6,488000.00),(37,13,8500.00,'2023-10-01','Mobile Money',3,86500.00),(38,13,8500.00,'2023-11-01','Mobile Money',3,78000.00),(39,13,8500.00,'2023-12-01','Mobile Money',3,69500.00),(40,15,24000.00,'2023-11-01','Bank',6,256000.00),(41,15,24000.00,'2023-12-01','Bank',6,232000.00),(42,16,26000.00,'2023-12-01','Bank',3,824000.00),(43,18,7500.00,'2023-12-15','Mobile Money',6,77500.00),(44,19,52000.00,'2023-12-21','Bank',3,2748000.00),(45,8,15000.00,'2024-01-05','Bank',3,1035000.00),(46,8,10000.00,'2024-01-20','Mobile Money',3,1025000.00),(47,10,25000.00,'2024-01-10','Bank',3,2275000.00),(48,6,25000.00,'2024-01-05','Bank',3,575000.00),(49,6,25000.00,'2024-01-25','Bank',3,550000.00),(50,7,5000.00,'2024-01-02','Mobile Money',6,37000.00),(51,7,3000.00,'2024-01-15','Cash',6,34000.00),(52,9,15000.00,'2024-01-01','Mobile Money',6,125000.00),(53,9,7000.00,'2024-01-15','Mobile Money',6,118000.00),(54,11,28000.00,'2024-01-01','Bank',6,460000.00),(55,13,10000.00,'2024-01-01','Mobile Money',3,59500.00),(56,13,10000.00,'2024-01-01','Mobile Money',3,49500.00),(57,15,24000.00,'2024-01-01','Bank',6,208000.00),(58,16,26000.00,'2024-01-01','Bank',3,798000.00),(59,18,7500.00,'2024-01-01','Mobile Money',6,70000.00),(60,19,52000.00,'2024-01-01','Bank',3,2696000.00);
/*!40000 ALTER TABLE `LoanRepayments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoanSchedule`
--

DROP TABLE IF EXISTS `LoanSchedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoanSchedule` (
  `ScheduleID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `InstallmentNumber` int NOT NULL,
  `InstallmentAmount` decimal(15,2) NOT NULL,
  `PrincipalComponent` decimal(15,2) NOT NULL,
  `InterestComponent` decimal(15,2) NOT NULL,
  `DueDate` date NOT NULL,
  `PaidFlag` tinyint(1) DEFAULT '0',
  `ArrearsFlag` tinyint(1) DEFAULT '0',
  `InstallmentStatus` enum('Pending','Overdue','Settled') DEFAULT 'Pending',
  PRIMARY KEY (`ScheduleID`),
  KEY `LoanID` (`LoanID`),
  CONSTRAINT `loanschedule_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoanSchedule`
--

LOCK TABLES `LoanSchedule` WRITE;
/*!40000 ALTER TABLE `LoanSchedule` DISABLE KEYS */;
INSERT INTO `LoanSchedule` VALUES (1,8,1,30000.00,25000.00,5000.00,'2023-08-01',1,0,'Settled'),(2,8,2,30000.00,25000.00,5000.00,'2023-09-01',1,0,'Settled'),(3,8,3,30000.00,25000.00,5000.00,'2023-10-01',1,0,'Settled'),(4,8,4,30000.00,25000.00,5000.00,'2023-11-01',1,0,'Settled'),(5,8,5,30000.00,25000.00,5000.00,'2023-12-01',1,0,'Settled'),(6,8,6,30000.00,25000.00,5000.00,'2024-01-01',0,1,'Overdue'),(7,8,7,30000.00,25000.00,5000.00,'2024-02-01',0,0,'Pending'),(8,10,1,50000.00,42000.00,8000.00,'2023-09-01',1,0,'Settled'),(9,10,2,50000.00,42000.00,8000.00,'2023-10-01',1,0,'Settled'),(10,10,3,50000.00,42000.00,8000.00,'2023-11-01',1,0,'Settled'),(11,10,4,50000.00,42000.00,8000.00,'2023-12-01',1,0,'Settled'),(12,10,5,50000.00,42000.00,8000.00,'2024-01-01',0,1,'Overdue'),(13,10,6,50000.00,42000.00,8000.00,'2024-02-01',0,0,'Pending'),(14,6,1,25000.00,21000.00,4000.00,'2023-07-01',1,0,'Settled'),(15,6,2,25000.00,21000.00,4000.00,'2023-08-01',1,0,'Settled'),(16,6,3,25000.00,21000.00,4000.00,'2023-09-01',1,0,'Settled'),(17,6,4,25000.00,21000.00,4000.00,'2023-10-01',1,0,'Settled'),(18,6,5,25000.00,21000.00,4000.00,'2023-11-01',1,0,'Settled'),(19,6,6,25000.00,21000.00,4000.00,'2023-12-01',1,0,'Settled'),(20,6,7,25000.00,21000.00,4000.00,'2024-01-01',1,1,'Settled'),(21,6,8,25000.00,21000.00,4000.00,'2024-02-01',0,0,'Pending'),(22,13,1,8500.00,7000.00,1500.00,'2023-10-01',1,0,'Settled'),(23,13,2,8500.00,7000.00,1500.00,'2023-11-01',1,0,'Settled'),(24,13,3,8500.00,7000.00,1500.00,'2023-12-01',1,0,'Settled'),(25,13,4,8500.00,7000.00,1500.00,'2024-01-01',1,0,'Settled'),(26,13,5,8500.00,7000.00,1500.00,'2024-02-01',0,0,'Pending');
/*!40000 ALTER TABLE `LoanSchedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MemberDocuments`
--

DROP TABLE IF EXISTS `MemberDocuments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MemberDocuments` (
  `DocumentID` int NOT NULL AUTO_INCREMENT,
  `MemberID` int NOT NULL,
  `DocumentType` enum('National ID','Passport','KRA Pin','Bank Statement','Payslip','Business License','Other') NOT NULL,
  `DocumentNumber` varchar(50) DEFAULT NULL,
  `DocumentPath` varchar(255) DEFAULT NULL,
  `UploadDate` date NOT NULL,
  `ExpiryDate` date DEFAULT NULL,
  `VerificationStatus` enum('Pending','Verified','Rejected') DEFAULT 'Pending',
  `VerifiedBy` int DEFAULT NULL,
  `VerificationDate` date DEFAULT NULL,
  `Notes` text,
  PRIMARY KEY (`DocumentID`),
  KEY `MemberID` (`MemberID`),
  KEY `VerifiedBy` (`VerifiedBy`),
  CONSTRAINT `memberdocuments_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`),
  CONSTRAINT `memberdocuments_ibfk_2` FOREIGN KEY (`VerifiedBy`) REFERENCES `Users` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MemberDocuments`
--

LOCK TABLES `MemberDocuments` WRITE;
/*!40000 ALTER TABLE `MemberDocuments` DISABLE KEYS */;
INSERT INTO `MemberDocuments` VALUES (1,1,'National ID','22334455','/documents/ids/22334455.pdf','2020-01-15',NULL,'Verified',1,'2020-01-15',NULL),(2,1,'KRA Pin','A123456789B','/documents/kra/A123456789B.pdf','2020-01-15',NULL,'Verified',1,'2020-01-15',NULL),(3,2,'National ID','22334456','/documents/ids/22334456.pdf','2020-02-01',NULL,'Verified',1,'2020-02-01',NULL),(4,3,'National ID','22334457','/documents/ids/22334457.pdf','2020-03-15',NULL,'Verified',1,'2020-03-15',NULL),(5,4,'National ID','22334458','/documents/ids/22334458.pdf','2020-04-01',NULL,'Verified',1,'2020-04-01',NULL),(6,5,'National ID','22334459','/documents/ids/22334459.pdf','2020-05-15',NULL,'Verified',1,'2020-05-15',NULL);
/*!40000 ALTER TABLE `MemberDocuments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MemberNextOfKin`
--

DROP TABLE IF EXISTS `MemberNextOfKin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MemberNextOfKin` (
  `NextOfKinID` int NOT NULL AUTO_INCREMENT,
  `MemberID` int NOT NULL,
  `FullName` varchar(255) NOT NULL,
  `Relationship` enum('Spouse','Child','Parent','Sibling','Other') NOT NULL,
  `PhoneNumber` varchar(20) NOT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Address` text,
  `NationalID` varchar(20) DEFAULT NULL,
  `SharePercentage` decimal(5,2) DEFAULT NULL,
  `Status` enum('Active','Inactive') DEFAULT 'Active',
  PRIMARY KEY (`NextOfKinID`),
  KEY `MemberID` (`MemberID`),
  CONSTRAINT `membernextofkin_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MemberNextOfKin`
--

LOCK TABLES `MemberNextOfKin` WRITE;
/*!40000 ALTER TABLE `MemberNextOfKin` DISABLE KEYS */;
INSERT INTO `MemberNextOfKin` VALUES (1,1,'Jane Kimani','Spouse','+254722333444','jane.kimani@email.com','Nairobi, Kenya','33445566',100.00,'Active'),(2,2,'John Njeri','Spouse','+254722333445','john.njeri@email.com','Westlands, Nairobi','33445567',100.00,'Active'),(3,3,'Alice Omondi','Spouse','+254722333446','alice.omondi@email.com','Thika, Kenya','33445568',100.00,'Active'),(4,4,'Peter Wanjiku','Spouse','+254722333447','peter.wanjiku@email.com','Kisumu, Kenya','33445569',100.00,'Active'),(5,5,'Grace Kiprop','Spouse','+254722333448','grace.kiprop@email.com','Mombasa, Kenya','33445570',100.00,'Active');
/*!40000 ALTER TABLE `MemberNextOfKin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Members`
--

DROP TABLE IF EXISTS `Members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Members` (
  `MemberID` int NOT NULL AUTO_INCREMENT,
  `MemberNo` varchar(50) NOT NULL,
  `FirstName` varchar(100) DEFAULT NULL,
  `MiddleName` varchar(100) DEFAULT NULL,
  `LastName` varchar(100) DEFAULT NULL,
  `FullName` varchar(255) NOT NULL,
  `NationalID` varchar(50) NOT NULL,
  `DateOfBirth` date DEFAULT NULL,
  `Gender` varchar(20) DEFAULT NULL,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Address` text,
  `MembershipDate` date DEFAULT NULL,
  `Status` enum('Active','Inactive','Suspended') DEFAULT 'Active',
  `MemberType` enum('Individual','Group','Corporate') DEFAULT 'Individual',
  `AccountBalance` decimal(15,2) DEFAULT '0.00',
  `Shares` decimal(15,2) DEFAULT '0.00',
  `CreatedBy` int DEFAULT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `BranchID` int DEFAULT NULL,
  PRIMARY KEY (`MemberID`),
  UNIQUE KEY `MemberNo` (`MemberNo`),
  KEY `BranchID` (`BranchID`),
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`BranchID`) REFERENCES `Branches` (`BranchID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Members`
--

LOCK TABLES `Members` WRITE;
/*!40000 ALTER TABLE `Members` DISABLE KEYS */;
INSERT INTO `Members` VALUES (1,'M001/2020','Samuel','','Kimani','Samuel Kimani','22334455','1985-03-15','Male','+254722111222','samuel@email.com','Nairobi, Kenya','2020-01-15','Active','Individual',150000.00,50000.00,1,'2024-12-31 07:27:53',1),(2,'M002/2020','Elizabeth','','Njeri','Elizabeth Njeri','22334456','1990-06-20','Female','+254722111223','elizabeth@email.com','Westlands, Nairobi','2020-02-01','Active','Individual',250000.00,75000.00,1,'2024-12-31 07:27:53',2),(3,'M003/2020','Joseph','','Omondi','Joseph Omondi','22334457','1988-09-10','Male','+254722111224','joseph@email.com','Thika, Kenya','2020-03-15','Active','Individual',180000.00,60000.00,1,'2024-12-31 07:27:53',3),(4,'M004/2020','Catherine','','Wanjiku','Catherine Wanjiku','22334458','1992-12-05','Female','+254722111225','catherine@email.com','Kisumu, Kenya','2020-04-01','Active','Individual',300000.00,100000.00,1,'2024-12-31 07:27:53',4),(5,'M005/2020','Michael','','Kiprop','Michael Kiprop','22334459','1987-07-25','Male','+254722111226','michael@email.com','Mombasa, Kenya','2020-05-15','Active','Individual',200000.00,80000.00,1,'2024-12-31 07:27:53',5),(6,'M006/2020','Patrick','','Mutua','Patrick Mutua','22334460','1989-04-18','Male','+254722111227','patrick@email.com','Nairobi South B','2020-06-01','Active','Individual',280000.00,90000.00,1,'2024-12-31 07:32:26',1),(7,'M007/2020','Joyce','','Mwangi','Joyce Mwangi','22334461','1991-08-22','Female','+254722111228','joyce@email.com','Kileleshwa','2020-06-15','Active','Individual',320000.00,100000.00,1,'2024-12-31 07:32:26',2),(8,'M008/2020','Simon','','Karanja','Simon Karanja','22334462','1986-11-30','Male','+254722111229','simon@email.com','Thika Road','2020-07-01','Active','Individual',180000.00,60000.00,1,'2024-12-31 07:32:26',1),(9,'M009/2020','Ruth','','Adhiambo','Ruth Adhiambo','22334463','1993-02-14','Female','+254722111230','ruth@email.com','Kisumu CBD','2020-07-15','Active','Individual',250000.00,80000.00,1,'2024-12-31 07:32:26',4),(10,'M010/2020','Hassan','','Ali','Hassan Ali','22334464','1988-05-25','Male','+254722111231','hassan@email.com','Mombasa Old Town','2020-08-01','Active','Individual',300000.00,100000.00,1,'2024-12-31 07:32:26',5),(11,'M011/2020','Faith','','Mutinda','Faith Mutinda','22334465','1990-09-12','Female','+254722111232','faith@email.com','Westlands','2020-08-15','Active','Individual',220000.00,75000.00,1,'2024-12-31 07:32:26',2),(12,'M012/2020','George','','Omondi','George Omondi','22334466','1987-12-05','Male','+254722111233','george@email.com','Thika Town','2020-09-01','Active','Individual',280000.00,90000.00,1,'2024-12-31 07:32:26',3),(13,'M013/2020','Lucy','','Wambui','Lucy Wambui','22334467','1992-03-20','Female','+254722111234','lucy@email.com','Nairobi West','2020-09-15','Active','Individual',350000.00,120000.00,1,'2024-12-31 07:32:26',1),(14,'M014/2020','David','','Kipchoge','David Kipchoge','22334468','1985-06-30','Male','+254722111235','david@email.com','Kisumu West','2020-10-01','Active','Individual',400000.00,150000.00,1,'2024-12-31 07:32:26',4),(15,'M015/2020','Sarah','','Muthoni','Sarah Muthoni','22334469','1994-01-15','Female','+254722111236','sarah@email.com','Nyali','2020-10-15','Active','Individual',280000.00,90000.00,1,'2024-12-31 07:32:26',5),(16,'M016/2021','Peter','','Kamau','Peter Kamau','22334470','1989-07-22','Male','+254722111237','peter@email.com','Parklands','2021-01-15','Active','Individual',320000.00,100000.00,1,'2024-12-31 07:32:26',2),(17,'M017/2021','Jane','','Akinyi','Jane Akinyi','22334471','1991-11-08','Female','+254722111238','jane@email.com','Thika Road','2021-02-01','Active','Individual',250000.00,80000.00,1,'2024-12-31 07:32:26',3),(18,'M018/2021','Thomas','','Ochieng','Thomas Ochieng','22334472','1986-04-17','Male','+254722111239','thomas@email.com','Kisumu East','2021-02-15','Active','Individual',300000.00,100000.00,1,'2024-12-31 07:32:26',4),(19,'M019/2021','Grace','','Njeri','Grace Njeri','22334473','1993-08-25','Female','+254722111240','grace@email.com','Mombasa CBD','2021-03-01','Active','Individual',280000.00,90000.00,1,'2024-12-31 07:32:26',5),(20,'M020/2021','Daniel','','Mwangi','Daniel Mwangi','22334474','1988-12-10','Male','+254722111241','daniel@email.com','Kilimani','2021-03-15','Active','Individual',350000.00,120000.00,1,'2024-12-31 07:32:26',1);
/*!40000 ALTER TABLE `Members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PaymentMethods`
--

DROP TABLE IF EXISTS `PaymentMethods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PaymentMethods` (
  `PaymentMethodID` int NOT NULL AUTO_INCREMENT,
  `MemberID` int NOT NULL,
  `MethodType` enum('Bank Account','Mobile Money','Cash','Check') NOT NULL,
  `BankName` varchar(100) DEFAULT NULL,
  `AccountNumber` varchar(50) DEFAULT NULL,
  `BranchName` varchar(100) DEFAULT NULL,
  `MobileNumber` varchar(20) DEFAULT NULL,
  `IsDefault` tinyint(1) DEFAULT '0',
  `Status` enum('Active','Inactive') DEFAULT 'Active',
  `DateAdded` date NOT NULL,
  `LastUsed` date DEFAULT NULL,
  PRIMARY KEY (`PaymentMethodID`),
  KEY `MemberID` (`MemberID`),
  CONSTRAINT `paymentmethods_ibfk_1` FOREIGN KEY (`MemberID`) REFERENCES `Members` (`MemberID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PaymentMethods`
--

LOCK TABLES `PaymentMethods` WRITE;
/*!40000 ALTER TABLE `PaymentMethods` DISABLE KEYS */;
INSERT INTO `PaymentMethods` VALUES (1,1,'Bank Account','KCB Bank','1234567890','Nairobi Branch',NULL,1,'Active','2020-01-15',NULL),(2,1,'Mobile Money',NULL,NULL,NULL,'+254722111222',0,'Active','2020-01-15',NULL),(3,2,'Bank Account','Equity Bank','0987654321','Westlands Branch',NULL,1,'Active','2020-02-01',NULL),(4,3,'Mobile Money',NULL,NULL,NULL,'+254722111224',1,'Active','2020-03-15',NULL),(5,4,'Bank Account','Cooperative Bank','1122334455','Kisumu Branch',NULL,1,'Active','2020-04-01',NULL),(6,5,'Mobile Money',NULL,NULL,NULL,'+254722111226',1,'Active','2020-05-15',NULL);
/*!40000 ALTER TABLE `PaymentMethods` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PenaltyCharges`
--

DROP TABLE IF EXISTS `PenaltyCharges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PenaltyCharges` (
  `PenaltyChargeID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int DEFAULT NULL,
  `ChargeAmount` decimal(10,2) DEFAULT NULL,
  `ChargeDate` date DEFAULT NULL,
  `ChargeType` enum('Late Payment','Partial Payment','Default') DEFAULT NULL,
  `Status` enum('Active','Paid','Waived') DEFAULT NULL,
  `Description` text,
  PRIMARY KEY (`PenaltyChargeID`),
  KEY `LoanID` (`LoanID`),
  CONSTRAINT `penaltycharges_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PenaltyCharges`
--

LOCK TABLES `PenaltyCharges` WRITE;
/*!40000 ALTER TABLE `PenaltyCharges` DISABLE KEYS */;
INSERT INTO `PenaltyCharges` VALUES (1,8,3000.00,'2024-01-01','Late Payment','Active','Late payment penalty for December 2023'),(2,8,3000.00,'2024-01-15','Late Payment','Active','Additional penalty for continued default'),(3,10,5000.00,'2024-01-01','Late Payment','Active','Late payment penalty for December 2023'),(4,10,5000.00,'2024-01-15','Late Payment','Active','Additional penalty for continued default'),(5,6,1000.00,'2024-01-05','Late Payment','Active','Late payment penalty for January 2024'),(6,7,500.00,'2024-01-05','Partial Payment','Active','Penalty for incomplete payment');
/*!40000 ALTER TABLE `PenaltyCharges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PenaltyManagement`
--

DROP TABLE IF EXISTS `PenaltyManagement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PenaltyManagement` (
  `PenaltyID` int NOT NULL AUTO_INCREMENT,
  `LoanID` int NOT NULL,
  `PenaltyRate` decimal(5,2) NOT NULL,
  `GracePeriod` int NOT NULL,
  `PenaltyTriggerDays` int NOT NULL,
  `PenaltyFrequency` enum('Daily','Weekly','Monthly') NOT NULL,
  `PenaltyCap` decimal(15,2) NOT NULL,
  `AutoPenaltyFlag` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`PenaltyID`),
  KEY `LoanID` (`LoanID`),
  CONSTRAINT `penaltymanagement_ibfk_1` FOREIGN KEY (`LoanID`) REFERENCES `LoanApplications` (`LoanAppID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PenaltyManagement`
--

LOCK TABLES `PenaltyManagement` WRITE;
/*!40000 ALTER TABLE `PenaltyManagement` DISABLE KEYS */;
/*!40000 ALTER TABLE `PenaltyManagement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_configs`
--

DROP TABLE IF EXISTS `system_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(100) NOT NULL,
  `key` varchar(100) NOT NULL,
  `value` json NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_configs`
--

LOCK TABLES `system_configs` WRITE;
/*!40000 ALTER TABLE `system_configs` DISABLE KEYS */;
/*!40000 ALTER TABLE `system_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `FullName` varchar(255) NOT NULL,
  `Role` enum('Admin','Appraiser','Teller','LoanOfficer') NOT NULL,
  `Status` enum('Active','Inactive') DEFAULT 'Active',
  `BranchID` int DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `Username` (`Username`),
  KEY `BranchID` (`BranchID`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`BranchID`) REFERENCES `Branches` (`BranchID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'admin.john','hashed_password_1','John Kamau','Admin','Active',1),(2,'loan.mary','hashed_password_2','Mary Wanjiku','LoanOfficer','Active',1),(3,'teller.peter','hashed_password_3','Peter Ochieng','Teller','Active',1),(4,'app.jane','hashed_password_4','Jane Muthoni','Appraiser','Active',1),(5,'loan.james','hashed_password_5','James Kiprop','LoanOfficer','Active',2),(6,'teller.sarah','hashed_password_6','Sarah Akinyi','Teller','Active',2),(7,'loan.david','hashed_password_7','David Maina','LoanOfficer','Active',3),(8,'app.grace','hashed_password_8','Grace Njeri','Appraiser','Active',3),(9,'loan.daniel','hashed_password_9','Daniel Otieno','LoanOfficer','Active',4),(10,'teller.faith','hashed_password_10','Faith Adhiambo','Teller','Active',4),(11,'loan.alice','hashed_password_11','Alice Wairimu','LoanOfficer','Active',1),(12,'loan.brian','hashed_password_12','Brian Mutua','LoanOfficer','Active',1),(13,'loan.carol','hashed_password_13','Caroline Nyambura','LoanOfficer','Active',1),(14,'loan.dennis','hashed_password_14','Dennis Kiprono','LoanOfficer','Active',2),(15,'loan.esther','hashed_password_15','Esther Muthoni','LoanOfficer','Active',2),(16,'loan.felix','hashed_password_16','Felix Odhiambo','LoanOfficer','Active',2),(17,'loan.grace','hashed_password_17','Grace Wangari','LoanOfficer','Active',3),(18,'loan.henry','hashed_password_18','Henry Kamau','LoanOfficer','Active',3),(19,'loan.irene','hashed_password_19','Irene Njoki','LoanOfficer','Active',3),(20,'loan.john','hashed_password_20','John Otieno','LoanOfficer','Active',4),(21,'loan.kevin','hashed_password_21','Kevin Ouko','LoanOfficer','Active',4),(22,'loan.lucy','hashed_password_22','Lucy Akinyi','LoanOfficer','Active',4),(23,'loan.mark','hashed_password_23','Mark Hassan','LoanOfficer','Active',5),(24,'loan.nancy','hashed_password_24','Nancy Kadzo','LoanOfficer','Active',5),(25,'loan.omar','hashed_password_25','Omar Salim','LoanOfficer','Active',5);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-31  9:32:06
