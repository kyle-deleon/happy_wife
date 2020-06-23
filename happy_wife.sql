-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema happy_wife
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `happy_wife` ;

-- -----------------------------------------------------
-- Schema happy_wife
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `happy_wife` DEFAULT CHARACTER SET utf8 ;
USE `happy_wife` ;

-- -----------------------------------------------------
-- Table `happy_wife`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `happy_wife`.`users` ;

CREATE TABLE IF NOT EXISTS `happy_wife`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL DEFAULT NULL,
  `last_name` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `husband` TINYINT(1) NULL DEFAULT NULL,
  `wife` TINYINT(1) NULL DEFAULT NULL,
  `partnered` TINYINT(1) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `happy_wife`.`partnerships`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `happy_wife`.`partnerships` ;

CREATE TABLE IF NOT EXISTS `happy_wife`.`partnerships` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `partner_id` INT NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_partners_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_partners_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `happy_wife`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `happy_wife`.`tasks`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `happy_wife`.`tasks` ;

CREATE TABLE IF NOT EXISTS `happy_wife`.`tasks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `partnership_id` INT NOT NULL,
  `created_by_id` INT NULL DEFAULT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `value` VARCHAR(255) NULL DEFAULT NULL,
  `for_id` INT NULL DEFAULT NULL,
  `completed_by_id` INT NULL DEFAULT NULL,
  `completed` TINYINT(1) NULL DEFAULT NULL,
  `approved` TINYINT(1) NULL DEFAULT NULL,
  `task` TINYINT(1) NULL DEFAULT NULL,
  `reward` TINYINT(1) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_tasks_partners1_idx` (`partnership_id` ASC) VISIBLE,
  CONSTRAINT `fk_tasks_partners1`
    FOREIGN KEY (`partnership_id`)
    REFERENCES `happy_wife`.`partnerships` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 21
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
