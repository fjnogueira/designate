# Copyright 2014 eBay Inc.
#
# Author: Ron Rickard <rrickard@ebay.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from oslo_log import log as logging

from designate.i18n import _LI
from designate.backend import base


LOG = logging.getLogger(__name__)


class FakeBackend(base.PoolBackend):
    __plugin_name__ = 'fake'

    def create_domain(self, context, domain):
        LOG.info(_LI('Create Domain %r') % domain)

    def delete_domain(self, context, domain):
        LOG.info(_LI('Delete Domain %r') % domain)
