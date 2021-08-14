import boto3
from botocore.exceptions import ClientError

class CRUD(object):
    def __init__(self):
        self.db_name = 'dynamodb'
        self.dynamo = None
        self.valid_keys = ['story_id','story_description','story_related_pics','story_comments']

    def error_message(self,extra_info=None):
        result = {"message" : "Error",'extra_info':extra_info}
        return result
    
    def success_message(self):
        result = {"message" : "Success"}
        return result

    def connect(self):
        try: 
            self.dynamo = boto3.resource(self.db_name)
            return self.success_message()
        except Exception as e:
            print(e)
            return self.error_message('Unable to connect to database')

    def get_table(self):
        try:
            self.connect()
            if self.dynamo is None:
                return self.dynamo
            return self.dynamo.Table('tbo_story_info')
        except:
            return None

    def story_id_exists(self,table,story_id):
        try:
            item = table.get_item(Key={'story_id':story_id})
            print(story_id)
            print(item)
            if 'Item' not in item.keys():
                item = None
        except:
            item = None
        return item

    def return_idx(self,table,story_id,column_name,pic_url):
        try:
            item = table.get_item(Key={'story_id':story_id})
            if 'Item' not in item.keys():
                return -1
            list_of_photos = item['Item'][column_name]
            for i in range(len(list_of_photos)):
                if list_of_photos[i] == pic_url:
                    return i
        except:
            return -1
        return -1

    
    def insert_story(self,reqData):
        '''
        Inserts story to table
        reqData structure for insert 
        {
            'story_id' : 'string',
            'story_description' : 'string',
            'story_related_pics' : ['string urls'],
            'story_comments' : {'user_name+comment_time' : 'entire_comment'}
        }
        '''
        if len(set(list(reqData.keys())) & set(self.valid_keys)) == len(self.valid_keys):
            table = self.get_table()
            print(table)
            if table == None:
                return self.error_message("Table not found")
            check_flag = self.story_id_exists(table,reqData['story_id'])
            if check_flag!= None:
                return self.error_message("Table already present")
            table.put_item(Item=reqData)
            return self.success_message()
        else:
            return self.error_message('Error inserting story')

    def update_story(self,reqData):
        '''
        Updates story
        reqData structure for update
        {
            'story_id' : 'string',
            'field_updated': 'story_description' or 'story_related_pics' or 'story_comments',
            'new_value' : "value from front-end or {'user_name+comment_time' : 'entire_comment'}" 
        }
        '''
        #check if story is present
        table = self.get_table()
        if table is None:
            return self.error_message('Unable to connect to database')
        check_flag = self.story_id_exists(table,reqData['story_id'])
        if check_flag is None:
            return self.error_message('Story id does not exists')
        key = {'story_id' : check_flag['Item']['story_id']}
        updateExpression,expressionAttributeValues,expressionAttributeNames,conditionExpression = "",None,None,None
        if reqData['field_updated'] == 'story_description':
            updateExpression = "set " + reqData['field_updated'] + "=:stryDesc"
            expressionAttributeValues = {':stryDesc' : reqData['new_value']}
        elif reqData['field_updated'] == 'story_related_pics':
            updateExpression = "set "+ reqData['field_updated'] + "=list_append(" + reqData['field_updated'] + ", :elem)" 
            expressionAttributeValues = {":elem" : [reqData['new_value']]}
        elif reqData['field_updated'] == 'story_comments':
            updateExpression = "set "+ reqData['field_updated'] + ".#commentTime =:comment"
            expressionAttributeNames = {"#commentTime" : list(reqData['new_value'].keys())[0]}
            expressionAttributeValues = {":comment" : list(reqData['new_value'].values())[0]}
            conditionExpression = "attribute_not_exists("+reqData['field_updated']+".#commentTime)"
        else:
            return self.error_message('Unable to update since field unknown')
        try:
            if reqData['field_updated'] == 'story_comments':
                table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeNames = expressionAttributeNames,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ConditionExpression = conditionExpression
                )
            else:
                table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                )
            return self.success_message()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                table.update_item(
                        Key = key,
                        UpdateExpression = updateExpression,
                        ExpressionAttributeNames = expressionAttributeNames,
                        ExpressionAttributeValues = expressionAttributeValues,
                        ConditionExpression = "attribute_exists("+reqData['field_updated']+".#commentTime)"
                )
                return self.success_message()
            else:
                return self.error_message("Unable to update request") 
        except Exception as e:
            print(e)
            return self.error_message("Unable to update request") 

    def delete_story(self,reqData):
        '''
        reqData structure for delete
        {
            'story_id' : 'string',
            'field_delete': story_related_pics' or 'story_comments',
            'delete_value' : "value from front-end or {'user_name+comment_time' : 'entire_comment'}" 
        }
        '''
        #check if story is present
        table = self.get_table()
        if table is None:
            return self.error_message('Unable to connect to database')
        check_flag = self.story_id_exists(table,reqData['story_id'])
        if check_flag is None:
            return self.error_message('Story id does not exists')
        updateExpression,conditionExpression = None,None
        key = {'story_id' : check_flag['Item']['story_id']}
        if reqData['field_delete'] == 'story_comments':
            updateExpression = "REMOVE "+reqData['field_delete'] + ".#commentTime"
            expressionAttributeNames = {"#commentTime" : list(reqData['delete_value'].keys())[0]} 
            conditionExpression = "attribute_exists("+reqData['field_delete']+".#commentTime)"
        elif reqData['field_delete'] == 'story_related_pics':
            idx = self.return_idx(table,reqData['story_id'],'story_related_pics',reqData['delete_value'])
            if idx < 0:
                return self.error_message('Picture url not found')
            updateExpression = "REMOVE story_related_pics[%d]" % (idx)
        try:
            if reqData['field_delete'] == 'story_related_pics':
                table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression
                )
            else:
                table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeNames = expressionAttributeNames,
                    ConditionExpression = conditionExpression
                )
            return self.success_message()
        except Exception as e:
            print(e)
            return self.error_message("Error deleting")

    def select_story(self,story_id):
        table = self.get_table()
        if table is None:
            return self.error_message("Unable to connect to database")
        check_flag = self.story_id_exists(table,story_id)
        if check_flag is None:
            return self.error_message('Story id does not exists')
        try:
            response = table.get_item(Key = {'story_id' : story_id})
        except ClientError as e:
            return self.error_message(e.response['Error']['Message'])
        else:
            return response['Item']
        