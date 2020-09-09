#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include <math.h>
#include <time.h>
#include "mpi.h"


int myRank,noOfProcesses;
MPI_Status status;
MPI_Request request;
double *globalx,*globaly,*globalz;
int *sendCounts,*displacements;

struct particle{
    double id,x,y,z;
};

void swap (double *a, double *b)  {  
    double temp = *a;  
    *a = *b;  
    *b = temp;  
}

void randomize (double *X, double *Y, double *Z,int noOfPoints)  
{  
    srand (time(NULL));  

    for (int i = noOfPoints - 1; i > 0; i--)  
    {  
        // Pick a random index from 0 to i  
        int j = rand() % (i + 1);  
  
        // Swap arr[i] with the element  
        // at random index  
        swap(&X[i], &X[j]);
        swap(&Y[i], &Y[j]);
        swap(&Z[i], &Z[j]);  
    }  
}  

void initFile(char *fileName, int noOfProcesses){
    
    FILE *fptr;
    fptr = fopen(fileName, "a+");

    if(fptr == NULL){
      printf("Error!%s",fileName);
      exit(1);
    }
    fprintf(fptr,"Number of processes: %d\n",noOfProcesses);
    fclose(fptr);
}

void writeClusterData(char *fileName,int timeStamp,int noOfClusters,int *countPerCluster,double *clusterMeans){
    FILE *fptr;
    fptr = fopen(fileName, "a+");
    if(fptr == NULL){
      printf("Error!");
      exit(1);
    }

    int countClusters = 0;
    for(int i=0;i<noOfClusters;i++){
        if(countPerCluster[i]!=0)
            countClusters++;
    }    

    fprintf(fptr,"T%d:",timeStamp);
    fprintf(fptr,"%d:",countClusters);

    for(int i=0;i<noOfClusters*3;i+=3){
        if(countPerCluster[i/3]!=0){
            fprintf(fptr,"<%d,(",countPerCluster[i/3]);
            fprintf(fptr,"%.3lf,",clusterMeans[i]);
            fprintf(fptr,"%.3lf,",clusterMeans[i+1]);
            fprintf(fptr,"%.3lf)>",clusterMeans[i+2]);
            
        }
    }
    fprintf(fptr,"\n");

    fclose(fptr);
}

void writeFileTime(char *writeFilePath,double timeToPreprocess,double timeToProcess,double totalTime){
    FILE *fptr;
    fptr = fopen(writeFilePath, "a+");
    if(fptr == NULL){
      printf("Error!");
      exit(1);
    }

    fprintf(fptr,"Average time to pre-process: %lf\n",timeToPreprocess);
    fprintf(fptr,"Average time to process: %lf\n",timeToProcess);
    fprintf(fptr,"Total time: %lf\n",totalTime);
    fprintf(fptr,"\n");
    fclose(fptr);

}

void writeCSVTime(char *writeFilePath,int noOfProcesses, double timeToPreProcess,double timeToProcess, double totalTime){
    FILE *fptr;
    fptr = fopen(writeFilePath, "a+");
    if(fptr == NULL){
      printf("Error!");
      exit(1);
    }
    fprintf(fptr,"%d,AP,%lf\n",noOfProcesses,timeToProcess);
    fprintf(fptr,"%d,APP,%lf\n",noOfProcesses,timeToPreProcess);
    fprintf(fptr,"%d,TT,%lf\n",noOfProcesses,totalTime);

}

int readData(char *folderPath, int file){
    
    char fileId[10];
    char fileName[20] = "file";
    sprintf(fileId,"%d",file); 
    strcat(fileName,fileId);

    char fullPath[30] = "";
    strcat(fullPath,folderPath);
    strcat(fullPath,fileName);

    FILE * fp;
    fp = fopen(fullPath,"rb");  // r for read, b for binary
    if ( fp == NULL ){
        printf( "Could not open file %s\n",fullPath) ;
        return 1;
    }
    struct particle p1;

    int count = 0;
    while ( fread(&p1,sizeof(struct particle),1,fp)) {
        globalx[count] = p1.x;
        globaly[count] = p1.y;
        globalz[count] = p1.z;
        count++;
    }
    return count;
}

int* scatterData(double *localX, double *localY, double *localZ, int noOfParticles){
    
    sendCounts = (int *)malloc(sizeof(int *)*noOfProcesses);
    displacements = (int *)malloc(sizeof(int *)*noOfProcesses);
    displacements[0] = 0;
    int noOfParticlesLeft = noOfParticles;
    for(int i=0;i<noOfProcesses;i++){
        sendCounts[i] = noOfParticlesLeft/(noOfProcesses-i);
        displacements[i+1] = displacements[i] + sendCounts[i];
        noOfParticlesLeft = noOfParticlesLeft - sendCounts[i];
    }
    
    // scatter from root process 0
    MPI_Scatterv(globalx, sendCounts, displacements, MPI_DOUBLE, localX, sendCounts[myRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Scatterv(globaly, sendCounts, displacements, MPI_DOUBLE, localY, sendCounts[myRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Scatterv(globalz, sendCounts, displacements, MPI_DOUBLE, localZ, sendCounts[myRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);

    return sendCounts;

}

double * initClusterMeans(int noOfParticles,int noOfClusters){
    
    double *clusterMeans = (double *)malloc(sizeof(double)*noOfClusters*3);
    srand (time(NULL));  

    for(int i=0;i<noOfClusters*3;i+=3){
        int index = rand()%noOfParticles;

        clusterMeans[i] =  globalx[index];
        clusterMeans[i+1] =  globaly[index];
        clusterMeans[i+2] =  globalz[index];
    }

    return clusterMeans;
}

double getEucliDist(double x,double y,double z,double xc,double yc,double zc){
    double x2 = (x-xc)*(x-xc);
    double y2 = (y-yc)*(y-yc);
    double z2 = (z-zc)*(z-zc);
    return sqrt(x2+y2+z2);
}

int assignCluster(double x,double y,double z,double *clusterMeans,int noOfClusters){
    // assigned cluster id
    int assignedCId = -1;

    // minimum distance to any cluster so far
    double min_so_far = __INT_MAX__;

    for(int i=0;i<noOfClusters*3;i+=3){
        double dist = getEucliDist(x,y,z,clusterMeans[i],clusterMeans[i+1],clusterMeans[i+2]);

        // if point is closer to ith cluster assign cluster id
        if(dist<min_so_far){
            assignedCId = i;
            min_so_far = dist;
        }       
    }
    return assignedCId;
}


double * updateClusterMean(double *X, double*Y, double*Z, int *globalCId, int noOfClusters, int noOfParticles){
    double *clusterMean = (double *)malloc(sizeof(double)*noOfClusters*3);

    // printf("**********************update Mean************************************\n");
    

    for(int i=0,k=0;i<noOfClusters;i++,k+=3){
        // find average X,Y,Z for cluster i
        double avgX=0,avgY=0,avgZ=0;
        int count=0;
        for(int j=0;j<noOfParticles;j++){
            if((globalCId[j]/3)==i){
                avgX+=X[j];
                avgY+=Y[j];
                avgZ+=Z[j];
                count++;
            }
        }

        avgX/=count;
        avgY/=count;
        avgZ/=count;

        clusterMean[k] = avgX;
        clusterMean[k+1] = avgY;
        clusterMean[k+2] = avgZ;
    }

    return clusterMean;
}

void clusterData(double *localX, double *localY, double *localZ, double *clusterMeans, int *perProcessCount, int noOfClusters,int noOfParticles, int timeStamp,char *fileName){

    int *globalCId = (int *)malloc(sizeof(int)*noOfParticles);
    int *localCId = (int *)malloc(sizeof(int)*perProcessCount[myRank]);
    int countPerCluster[noOfClusters];
    int localDisplacements[noOfProcesses];

    localDisplacements[0] = 0;
    for(int i=1;i<noOfProcesses;i++){
        localDisplacements[i] = localDisplacements[i-1]+perProcessCount[i-1];   
    }
    
    int maxIterations = 100;
    while(maxIterations>0){
    
        // stores count of no of points assigned to a diferent cluster
        int localCount = 0;
        int globalCount = 0;

        // announce cluster means
        MPI_Bcast(clusterMeans, 3*noOfClusters, MPI_DOUBLE, 0, MPI_COMM_WORLD);

        // for every data point that a process has
        for(int i=0;i<perProcessCount[myRank];i++){
            // assign point to a cluster
            int id = assignCluster(localX[i],localY[i],localZ[i],clusterMeans,noOfClusters);

            // if cluster has changed increment counter
            if(id != localCId[i])
                localCount++;

            localCId[i] = id;
        }

        // let every process finish cluster assignment
        MPI_Barrier(MPI_COMM_WORLD);
       
        // gather cluster id of all points
        MPI_Gatherv(localCId, perProcessCount[myRank], MPI_INT, globalCId, perProcessCount, localDisplacements, MPI_INT, 0, MPI_COMM_WORLD);

        // calculate how many of all points are assigned to a different cluster
        MPI_Allreduce(&localCount,&globalCount,1,MPI_INT,MPI_SUM,MPI_COMM_WORLD);

        // count particles to each cluster
        if(myRank==0){
            // printf("reassigned count:%d\n",globalCount);
            for(int i=0;i<noOfClusters;i++){
                countPerCluster[i]=0;
            }
            
            for(int i=0;i<noOfParticles;i++){
                countPerCluster[globalCId[i]/3]++;
            }

        }

        // update cluster means
        if(myRank == 0)
            clusterMeans =  updateClusterMean(globalx,globaly,globalz,globalCId,noOfClusters,noOfParticles);
        
        maxIterations--;
        MPI_Barrier(MPI_COMM_WORLD);

        // if less than 1% particles are reassigned to a new cluster then k-means has converged
        if(globalCount<0.01*noOfParticles)
            break;

    }

    if(myRank==0)
        writeClusterData(fileName,timeStamp,noOfClusters,countPerCluster,clusterMeans);

    return;
}


int main(int argc, char *argv[]){
    MPI_Init( &argc, &argv );
    MPI_Comm_size(MPI_COMM_WORLD, &noOfProcesses);
    MPI_Comm_rank(MPI_COMM_WORLD, &myRank );

    //read input from argv 
    int noOfFiles = atoi(argv[1]);
    int noOfParticles = atoi(argv[2]);
    int noOfClusters = atoi(argv[3]);
    char *readFolder = argv[4];
    char *writeFilePath = argv[5];
    char *writeCsvFilePath = argv[6];

    // allocate memory to store particles
    globalx = (double *)malloc(sizeof(double *)*noOfParticles);
    globaly = (double *)malloc(sizeof(double *)*noOfParticles);
    globalz = (double *)malloc(sizeof(double *)*noOfParticles);

    // stores datapoints local to a process
    double *localX = (double *) malloc(sizeof(double)*ceil(noOfParticles/noOfProcesses));
    double *localY = (double *) malloc(sizeof(double)*ceil(noOfParticles/noOfProcesses));
    double *localZ = (double *) malloc(sizeof(double)*ceil(noOfParticles/noOfProcesses));
    double *clusterMeans = (double *)malloc(sizeof(double)*noOfClusters*3);
    int *perProcessCount;

    if(myRank==0)
        initFile(writeFilePath,noOfProcesses);

    double timeToPreProcess = 0,timeToProcess=0,totalTime=0,tic,toc;

    
    double ticT = MPI_Wtime();
    for(int i=0;i<noOfFiles;i++){
      

        // *******************************preprocessing data************************************
        tic = MPI_Wtime();
        // read file get count of particles and initialize x,y,z
        if (myRank == 0){
            printf("File%d \tprocesses:%d\n",i,noOfProcesses);  
            noOfParticles = readData(readFolder,i);   
        }
        // broadcat noOfParticles to all processses from root O
        MPI_Bcast(&noOfParticles, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

        // give data to every process to cluster
        perProcessCount = scatterData(localX, localY, localZ, noOfParticles);
    
        toc = MPI_Wtime();

        timeToPreProcess += (toc - tic);
        // *******************************preprocessing ends************************************


        // *******************************clustering data***************************************
        tic = MPI_Wtime();
        if(myRank==0){
            clusterMeans = initClusterMeans(noOfParticles,noOfClusters);
        }

        // cluster datapoints
        clusterData(localX,localY,localZ,clusterMeans,perProcessCount,noOfClusters,noOfParticles,i,writeFilePath);
        toc = MPI_Wtime();
        timeToProcess += (toc - tic); 
        // *******************************clustering ends***************************************

        // let every process complete one timestamp then only start next step
        MPI_Barrier(MPI_COMM_WORLD);
    }
    double tocT = MPI_Wtime();

    totalTime = tocT-ticT;
    if(myRank == 0){
        writeFileTime(writeFilePath,timeToPreProcess/noOfFiles,timeToProcess/noOfFiles,totalTime);
        writeCSVTime(writeCsvFilePath,noOfProcesses,timeToPreProcess/noOfFiles,timeToProcess/noOfFiles,totalTime);
    }
    
    MPI_Barrier(MPI_COMM_WORLD);
    return 0;
}
