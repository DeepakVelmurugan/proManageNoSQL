node{
    def ec2ip = "ssh -o  StrictHostKeyChecking=no ec2-user@3.108.184.126"
    stage('Git pull'){
       sshagent(['ec2-user']) {
           def clone = "${ec2ip} cd proManageNoSQL || ${ec2ip} git clone https://github.com/DeepakVelmurugan/proManageNoSQL.git;"
           sh "${ec2ip} sudo yum install git-all -y"
           sh "${clone}"
           sh "${ec2ip} git --git-dir=proManageNoSQL/.git pull"
           sh "${ec2ip}  mv * proManageNoSQL || echo Cannot copy directory"
       }
    }
    stage('Build docker image'){
        sshagent(['ec2-user']) {
            withCredentials([usernamePassword(credentialsId: 'accessID', passwordVariable: 'ACCESSKEY', usernameVariable: 'ACCESSID')]) {
                sh "${ec2ip} docker build --build-arg AWS_ACCESS_KEY_ID=$ACCESSID --build-arg AWS_SECRET_ACCESS_KEY=$ACCESSKEY -t deepakvelmurugan/promanagenosql:latest --file proManageNoSQL/Dockerfile ."    
            }
        }
    }
    stage('Push Docker Image'){
        sshagent(['ec2-user']) {
            withCredentials([usernamePassword(credentialsId: 'dockerCred', passwordVariable: 'dockerpwd', usernameVariable: 'deepakvelmurugan')]) {
                sh "${ec2ip} docker login -u ${deepakvelmurugan} -p ${dockerpwd}"
            }
            sh "${ec2ip} docker push deepakvelmurugan/promanagenosql"
        }
    }
    stage('Run Container on DEV server'){
        sshagent(['ec2-user']) {
            def dockerRemove = "docker rm -f nosqlimage || echo Not found"
            def dockerRun = "docker run -p 8080:8000 -d --name nosqlimage deepakvelmurugan/promanagenosql"
            sh "${ec2ip} ${dockerRemove}"
            sh "${ec2ip} ${dockerRun}"
        }
    }
}