# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
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
import flask
from oslo_log import log as logging

from designate import schema
from designate.api.v1 import load_values
from designate.central import rpcapi as central_rpcapi
from designate import objects


LOG = logging.getLogger(__name__)
blueprint = flask.Blueprint('domains', __name__)
domain_schema = schema.Schema('v1', 'domain')
domains_schema = schema.Schema('v1', 'domains')
servers_schema = schema.Schema('v1', 'servers')


def _poolattribute_to_server(pool_attribute):
    server_values = {
        'id': pool_attribute.id,
        'created_at': pool_attribute.created_at,
        'updated_at': pool_attribute.updated_at,
        'version': pool_attribute.version,
        'name': pool_attribute.value
    }

    server = objects.Server(**server_values)
    return server


@blueprint.route('/schemas/domain', methods=['GET'])
def get_domain_schema():
    return flask.jsonify(domain_schema.raw)


@blueprint.route('/schemas/domains', methods=['GET'])
def get_domains_schema():
    return flask.jsonify(domains_schema.raw)


@blueprint.route('/domains', methods=['POST'])
def create_domain():
    valid_attributes = ['name', 'email', 'ttl', 'description']
    context = flask.request.environ.get('context')

    values = load_values(flask.request, valid_attributes)

    domain_schema.validate(values)

    central_api = central_rpcapi.CentralAPI.get_instance()
    domain = central_api.create_domain(context, objects.Domain(**values))

    response = flask.jsonify(domain_schema.filter(domain))
    response.status_int = 201
    response.location = flask.url_for('.get_domain', domain_id=domain['id'])

    return response


@blueprint.route('/domains', methods=['GET'])
def get_domains():
    context = flask.request.environ.get('context')

    central_api = central_rpcapi.CentralAPI.get_instance()
    domains = central_api.find_domains(context)

    return flask.jsonify(domains_schema.filter({'domains': domains}))


@blueprint.route('/domains/<uuid:domain_id>', methods=['GET'])
def get_domain(domain_id):
    context = flask.request.environ.get('context')

    central_api = central_rpcapi.CentralAPI.get_instance()
    domain = central_api.get_domain(context, domain_id)

    return flask.jsonify(domain_schema.filter(domain))


@blueprint.route('/domains/<uuid:domain_id>', methods=['PUT'])
def update_domain(domain_id):
    context = flask.request.environ.get('context')
    values = flask.request.json

    central_api = central_rpcapi.CentralAPI.get_instance()

    # Fetch the existing resource
    domain = central_api.get_domain(context, domain_id)

    # Prepare a dict of fields for validation
    domain_data = domain_schema.filter(domain)
    domain_data.update(values)

    # Validate the new set of data
    domain_schema.validate(domain_data)

    # Update and persist the resource
    domain.update(values)
    domain = central_api.update_domain(context, domain)

    return flask.jsonify(domain_schema.filter(domain))


@blueprint.route('/domains/<uuid:domain_id>', methods=['DELETE'])
def delete_domain(domain_id):
    context = flask.request.environ.get('context')

    central_api = central_rpcapi.CentralAPI.get_instance()
    central_api.delete_domain(context, domain_id)

    return flask.Response(status=200)


@blueprint.route('/domains/<uuid:domain_id>/servers', methods=['GET'])
def get_domain_servers(domain_id):
    context = flask.request.environ.get('context')

    central_api = central_rpcapi.CentralAPI.get_instance()

    nameservers = central_api.get_domain_servers(context, domain_id)

    servers = objects.ServerList()

    for ns in nameservers:
        servers.append(_poolattribute_to_server(ns))

    return flask.jsonify(servers_schema.filter({'servers': servers}))
