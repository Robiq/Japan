
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
#include <unistd.h> // read(), write(), getcwd()
#include <stdlib.h>
#include <sys/stat.h> // stat struct and stat()
#include <regex.h>

#define BUF_SIZE 100000
#define FILENAME_SIZE 100
#define VERSION_SIZE 9
#define PORT 7000
#define PATH_SIZE 1024

//ROBIN LUNDE 81625481

int main()
{
	int sockfd, acceptfd; 
	int len,count=0,i; 
	char buf[BUF_SIZE];
	char fileName[FILENAME_SIZE];
	struct sockaddr_in server, client; 
	FILE *in;
	struct stat sb;

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
		char* httpVer;
		listen(sockfd, 5);
		/* establish connection between a client host */
		memset(&client, 0, sizeof(client)); 
		len = sizeof(client); 
		acceptfd = accept(sockfd, (struct sockaddr *) &client, &len);
		/* read data */
	    read(acceptfd, buf, sizeof(buf));
		buf[strlen(buf)-2] = '\0';  //The buf has 2 abundant characters
		
		/*process GET /<file name> command */
		//Do regex lookup to make sure we have a correct HTTP-request
		regex_t regex;
		int ret;
		ret=regcomp(&regex, "HTTP.*", 0);
		if(ret){
			printf("Critical server error on line 62\n");
			exit(-1);
		}
		ret=regexec(&regex, buf, 0, NULL, 0);
		//Not a correct format of string
		if(ret){
			write(acceptfd, "400 Bad Request\n", 17);
			close(acceptfd);
			continue;
		}

		//Is the 5 first characters of the command is GET /?  
		if(strncmp(buf,"GET /",5) == 0) {



		     //Store filename and HTTP version
		    for(i=5;i<strlen(buf);i++)
		      {
		      	if(buf[i] == ' ')
		      		break;
				fileName[count++] = buf[i];
		      }
		    fileName[count] = '\0';
			
		    httpVer = &(buf[i]);
	
		     //If command is GET / the "index.html" file will be sent
		    if(strlen(fileName) == 0)
		      strcpy(fileName,"index.html");
		    
		  	
		    //Check if file exsist. If not, throw error.
		  	//Get working directory
			char* path = malloc((size_t) PATH_SIZE);
		  	path = getcwd(path, PATH_SIZE);
		  	
		  	//Check if the file exists in the directory		    
		    strncat(path, "/", 2);
		    strncat(path,fileName,strlen(fileName));

		    //If stat returns -1, file does not exist
		    if(stat (path, &sb) == -1){
		      write(acceptfd, httpVer+1, strlen(httpVer));
		      write(acceptfd," 404 not found\n",16);
		    
			//If the command is GET/<file name> <file name> will be sent
		    }else{               
		    	//File exists, so we open it, read it and send it to the socket.
		    	in = fopen(fileName,"r");
			    
			    write(acceptfd, httpVer+1, strlen(httpVer));
				write(acceptfd, " 200 OK\n", 8);
				char* tempbuf = malloc(BUF_SIZE);
				//Get information stored in file and send it
				fgets(tempbuf,BUF_SIZE,in);
				write(acceptfd,tempbuf,strlen(buf));
				
		   		fclose(in);
				free(tempbuf);
				write(acceptfd,"\n",2);
		    }
		    free(path);
		   //If an unsupported command is given as input, return error.
		} else{
			//Find length of HTTP request
			for(i=strlen(buf);i>=0;i--){
				if(buf[i]==' ')	break;
			}

			//Give address of HTTP request to pointer
			httpVer=&(buf[++i]);

			//Return error
			write(acceptfd, httpVer, strlen(httpVer));
			write(acceptfd, " 501 Not Implemented\n", 22);
		} 
		/*Close connection*/
		close(acceptfd);
		
	}
	close(sockfd); 
}