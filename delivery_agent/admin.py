from django.contrib import admin

from delivery_agent.models import (AcceptedOrder, AdditionalDetail, Document, ActivationTime, AgentCashEntry)

admin.site.register(AdditionalDetail)
admin.site.register(AcceptedOrder)
admin.site.register(Document)
admin.site.register(ActivationTime)
admin.site.register(AgentCashEntry)
