-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 29, 2025 at 11:25 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `habitsphere`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `bio` text DEFAULT NULL,
  `profile_pic_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fullname`, `email`, `password`, `bio`, `profile_pic_url`, `created_at`) VALUES
(1, 'PRIYANSH', 'priyansh.tailor39@gmail.com', 'scrypt:32768:8:1$RYUb3kjsK3CY0x4p$eed6b5ee571ac6d8c0ff01b82818276ca7bbc2d39fe988d3ded52c7ddb202014e2f519ed361e2a8e1ac933b80bd0e8cbc15ea04d523709a02cd6552c0bd4bf2f', NULL, '/images/user_1_insurance.jpg', '2025-06-27 08:27:53'),
(2, 'Vidhi Trivedi', 'vidhi@gmail.com', 'scrypt:32768:8:1$vIs2heS3kxO2oS7Y$815e60ecfc1feea375cea544611394a82e238c1bb05f6819b413d2804675e67ad4ac1a7c7a8f400668536ec45a2e31836b1fdfc2cd223e3c2d41a3e2054535b7', NULL, '/images/1751029284_images.jpeg', '2025-06-27 13:00:46');

-- --------------------------------------------------------

--
-- Table structure for table `user_habits`
--

CREATE TABLE `user_habits` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `habit` varchar(255) DEFAULT NULL,
  `icon` varchar(10) DEFAULT NULL,
  `preferred_time` varchar(50) DEFAULT NULL,
  `scheduled_day` varchar(20) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `done_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `user_habits`
--

INSERT INTO `user_habits` (`id`, `user_id`, `habit`, `icon`, `preferred_time`, `scheduled_day`, `status`, `done_at`) VALUES
(1, 1, 'write a poem', '✍️', 'Anytime', NULL, 'Done', '2025-06-29 09:10:54'),
(2, 1, 'write short story', '✍️', 'Anytime', NULL, 'Skipped', NULL),
(3, 1, 'play music', '🧘', 'Anytime', NULL, 'Done', '2025-06-29 09:20:55');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_habits`
--
ALTER TABLE `user_habits`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user_habits`
--
ALTER TABLE `user_habits`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
