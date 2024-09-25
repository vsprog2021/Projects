#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 2908
#define MAX_NAME_LEN 16

int main(int argc, char *argv[]) {
  int client_socket;
  struct sockaddr_in server_address;
  char name[MAX_NAME_LEN];
  char command[100];
  int num_bytes;
  int count;
  char msg[100];
  int rrd=0;
  int k=0, i=0;

  // Create the client socket
  client_socket = socket(AF_INET, SOCK_STREAM, 0);
  if (client_socket < 0) {
    perror("Error creating socket\n");
    exit(1);
  }

  // Set up the server address
  memset(&server_address, 0, sizeof(server_address));
  server_address.sin_family = AF_INET;
  //server_address.sin_addr.s_addr = inet_addr("127.0.0.1");
  server_address.sin_addr.s_addr = inet_addr("192.168.1.150");
  server_address.sin_port = htons(PORT);

  // Connect to the server
  if (connect(client_socket, (struct sockaddr *) &server_address, sizeof(server_address)) < 0) {
    perror("Error connecting to server\n");
    exit(1);
  }

  printf("Enter your name: ");
  fgets(name, MAX_NAME_LEN, stdin);
  name[strlen(name) - 1] = '\0';
  write(client_socket, name, strlen(name));
  
  bzero(&msg,100);
  read(client_socket,msg,100);
  printf("%s\n",msg);
    
  while (1) {
  
    fflush(stdout);
    fflush(stdin);  
    memset(&command,0,100);
    
    printf("Introdu o comanda sau foloseste comanda help: ");
    fgets(command,100,stdin);
    command[strlen(command) - 1] = '\0';
    num_bytes=write(client_socket, command, strlen(command));
    
    if (num_bytes < 0) {
      perror("Error writing to socket");
      exit(1);
    }
    
    if (strcmp(command, "quit") == 0)
      break;
    
    memset(&command,0,100);
    num_bytes=read(client_socket, &command, sizeof(command));
    if (num_bytes < 0) {
      perror("Error reading from socket");
      exit(1);
    }   
    printf("%s\n", command);
    
    
    fflush(stdout);
    fflush(stdin);
   
  }//while

  close(client_socket);

  return 0;
}

