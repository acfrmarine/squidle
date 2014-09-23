import logging
from guardian.shortcuts import assign

logger = logging.getLogger(__name__)


# default permissions for collection objects
def apply_pointannotationset_permissions(user, pointannotationset):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to campaign: " + pointannotationset.name)

    assign('annotations.view_pointannotationset', user, pointannotationset)
    assign('annotations.update_pointannotationset', user, pointannotationset)
    assign('annotations.delete_pointannotationset', user, pointannotationset)

    #assign view permissions to the Anonymous user
    #logger.debug("Making campaign public: " + pointannotationset.name)

    # Allow public group to view pointannotationsets
    #public_group, created = Group.objects.get_or_create(name='Public')
    #assign('view_pointannotationset', public_group, pointannotationset)