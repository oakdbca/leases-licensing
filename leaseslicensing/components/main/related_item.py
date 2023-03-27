from rest_framework import serializers


class RelatedItem:
    def __init__(self, model_name='', identifier='', descriptor='',
            action_url='', type=''):
        self.model_name = model_name
        self.identifier = identifier
        self.descriptor = descriptor
        self.action_url = action_url
        self.type = type



class RelatedItemsSerializer(serializers.Serializer):
    model_name = serializers.CharField()
    identifier = serializers.CharField()
    descriptor = serializers.CharField()
    action_url = serializers.CharField(allow_blank=True)
    type = serializers.CharField()
