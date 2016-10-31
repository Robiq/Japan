
/*
 * ws.c : a modified version of  echo_server.c 
 * echo server program for Ubiquitous System Architecture. 
 * Created by a student
 */

#include <sys/types.h>  // socket(), listen(), accept(), read(), write()
#include <sys/socket.h> // socket(), listen(), accept(), read(), write()
#include <sys/uio.h>    // read(), write()

#include <netinet/in.h> // struct sockaddr_in 

#include <string.h> // memset()
#include <stdio.h>  // printf() 
#include <unistd.h> // read(), write()
#include <stdlib.h>

int main()
{
	int sockfd, acceptfd; 
	int len,count,i; 
	char buf[100000];
	char fileName[100];
	struct sockaddr_in server, client; 

	FILE *in;
      
	/* create socket */
	sockfd = socket(PF_INET, SOCK_STREAM, 0);

	/* initialize socket */
	memset(&server, 0, sizeof(server)); 
	server.sin_family = PF_INET; 
	server.sin_port   = htons(7000); 
	server.sin_addr.s_addr = htonl(INADDR_ANY); 
	bind(sockfd, (struct sockaddr *)&server, sizeof(struct sockaddr_in));
    while(1){ //The server is always open

	/* wait here until client tries to connect */
	listen(sockfd, 5);

	/* establish connection between a client host */
	memset(&client, 0, sizeof(client)); 
	len = sizeof(client); 
	acceptfd = accept(sockfd, (struct sockaddr *) &client, &len);

	/* read data */
       	read(acceptfd, buf, sizeof(buf));
	buf[strlen(buf)-2] = '\0';  //The buf has 2 abundant characters

	/*process GET/<file name> command */
	if(strncmp(buf,"GET/",4) == 0)   //Is the 4 first characters of the command is GET/?  
	  {
	    for(i=4;i<strlen(buf);i++)
	      {
		fileName[count++] = buf[i];
	      }
	    fileName[count] = '\0';
	    if(strlen(fileName) == 0) //If command is GET/ the "index.html" file will be sent
	      strcpy(fileName,"index.html");
	    in = fopen(fileName,"r");
	    if(in == NULL){
	      write(acceptfd,"Error,file not found\n",22);
	      exit(0);
	    }
	    else{               //If the command is GET/<file name> <file name> will be sent
	    while(!feof(in)){
	      fread(buf,1,sizeof(buf),in);
	      write(acceptfd,buf,strlen(buf));
		}
	    write(acceptfd,"\n",2);
	    }
	}
	/*Close connection*/
	close(acceptfd);
      } 
	close(sockfd); 
}
