
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

#define BUF_SIZE 100000
#define FILENAME_SIZE 100
#define VERSION_SIZE 9
#define PORT 7000

int main(void)
{
	int sockfd, acceptfd; 
	int len,count,i; 
	char buf[BUF_SIZE];
	char fileName[FILENAME_SIZE];
	char httpVer[VERSION_SIZE];
	struct sockaddr_in server, client; 
	FILE *in;
      
	/* create socket */
	sockfd = socket(PF_INET, SOCK_STREAM, 0);
	/* initialize socket */
	memset(&server, 0, sizeof(server)); 
	server.sin_family = PF_INET; 
	server.sin_port   = htons(PORT); 
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
		//TODO include http version all the time
		/*process GET /<file name> command */

		 //Is the 5 first characters of the command is GET /?  
		if(strncmp(buf,"GET /",5) == 0) {
		    for(i=5;i<strlen(buf);i++)
		      {
		      	if(buf[i++] == ' ')
		      		break;
				fileName[count++] = buf[i];
		      }
		    fileName[count] = '\0';
		    int j;
		    for(j=i;j<strlen(buf);j++){
				httpVer[j-i] = buf[j]; 	
		    }
		    httpVer[j+1] = '\0';

		    printf("%s\n", fileName);

		     //If command is GET / the "index.html" file will be sent
		    if(strlen(fileName) == 0)
		      strcpy(fileName,"index.html");
		    
		    in = fopen(fileName,"r");
		    if(in == NULL){
		      write(acceptfd, httpVer, strlen(httpVer));
		      write(acceptfd," 404 not found\n",16);
		      exit(0);
		    
			//If the command is GET/<file name> <file name> will be sent
		    }else{               
		    	while(!feof(in)){
				    //Check if file exsist. If not, throw error. TODO
			      	write(acceptfd, httpVer, strlen(httpVer));
				    write(acceptfd, " 200 OK\n", 8);
				   //FIX fread and BUF! Already used in socket, then written to.
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