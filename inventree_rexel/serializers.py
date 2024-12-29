from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from company.models import Company
from part.models import Part
from part.serializers import PartBriefSerializer


class OrderHistoryRequestSerializer(serializers.Serializer):
    """Serializer voor het aanvragen van geschiedenisdata op basis van een zoekopdracht."""

    query = serializers.CharField(
        label=_('Search Query'),
        required=True,
        help_text=_('Enter a search term to filter order history'),
    )
    
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), many=False, required=False, label=_('Company')
    )

    part = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(), many=False, required=False, label=_('Part')
    )

    # Dit zijn de velden die je niet meer nodig hebt
    # start_date = serializers.DateField(label=_('Start Date'), required=True)
    # end_date = serializers.DateField(label=_('End Date'), required=True)
    # period = serializers.ChoiceField(
    #     label=_('Period'),
    #     choices=[('M', _('Month')), ('Q', _('Quarter')), ('Y', _('Year'))],
    #     required=False,
    #     default='D',
    #     help_text=_('Group order data by this period'),
    # )
    # order_type = serializers.ChoiceField(
    #     label=_('Order Type'),
    #     choices=[('build', _('Build Order')), ('purchase', _('Purchase Order')), ('sales', _('Sales Order')), ('return', _('Return Order'))],
    #     help_text=_('Filter order data by this type'),
    # )
    # export = serializers.ChoiceField(
    #     choices=[(choice, choice) for choice in ['csv', 'tsv', 'xls', 'xlsx']],
    #     required=False,
    #     label=_('Export Format')
    # )


class OrderHistoryItemSerializer(serializers.Serializer):
    """Serializer voor een enkel item in de OrderHistoryResponseSerializer."""

    class Meta:
        fields = ['date', 'quantity']

    date = serializers.DateField(read_only=True)
    quantity = serializers.FloatField(read_only=True)


class OrderHistoryResponseSerializer(serializers.Serializer):
    """Serializer voor het retourneren van geschiedenisdata van de OrderHistory plugin."""

    class Meta:
        fields = ['part', 'history']

    part = PartBriefSerializer(read_only=True, many=False)
    history = OrderHistoryItemSerializer(many=True, read_only=True)
