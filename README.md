# File_Transfer_System_be
Overview

This project implements a multi-client file transfer system where multiple clients can upload files to a server, and the server transmits them back with integrity verification using checksums. The system also handles network errors like packet drops and corruption with retransmission logic.

Features

Supports multiple clients concurrently
Transfers files in fixed-size chunks (e.g., 1024 bytes)
Ensures data integrity using SHA-256 checksums
Simulates packet loss and corruption with automatic retransmission
Uses TCP sockets for reliable communication

Requirements

Python 3.x
Required Libraries: socket, threading, hashlib, random

How It Works

Clients upload a file to the server.
The server splits it into chunks and computes a checksum.
The server transmits chunks back to the client.
The client reassembles the file and verifies its integrity.
If errors are detected, missing chunks are re-requested.
