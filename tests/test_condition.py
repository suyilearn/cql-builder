import unittest
from unittest import TestCase
from datetime import timedelta
from cql_builder.base import ValidationError
from cql_builder.condition import AllEqual, In, Where, Using
from cql_builder.condition import eq, gt, gte, lt, lte

class TestComparison(TestCase):

	def test_eq(self):
		name, value = 'x', 13
		comp = eq(name, value)
		self.assertEquals(comp.cql, '{}=%s'.format(name))
		self.assertEquals(comp.values, [value])

	def test_gt(self):
		name, value = 'x', 13
		comp = gt(name, value)
		self.assertEquals(comp.cql, '{}>%s'.format(name))
		self.assertEquals(comp.values, [value])

	def test_gte(self):
		name, value = 'x', 13
		comp = gte(name, value)
		self.assertEquals(comp.cql, '{}>=%s'.format(name))
		self.assertEquals(comp.values, [value])

	def test_lt(self):
		name, value = 'x', 13
		comp = lt(name, value)
		self.assertEquals(comp.cql, '{}<%s'.format(name))
		self.assertEquals(comp.values, [value])

	def test_lte(self):
		name, value = 'x', 13
		comp = lte(name, value)
		self.assertEquals(comp.cql, '{}<=%s'.format(name))
		self.assertEquals(comp.values, [value])

class TestAll(TestCase):

	def test_eq_single(self):
		kwargs = {'last': 'foo'}
		cond = AllEqual(**kwargs)
		self.assertEquals(cond.cql, '{}=%s'.format(*kwargs.keys()))
		self.assertEquals(cond.values, kwargs.values())

	def test_eq_multi(self):
		kwargs = {'first': 'foo', 'last': 'bar'}
		cond = AllEqual(**kwargs)
		self.assertEquals(cond.cql, '{}=%s AND {}=%s'.format(*kwargs.keys()))
		self.assertEquals(cond.values, kwargs.values())

class TestIn(TestCase):

	def test_list_value(self):
		name, value = 'name', ['foo', 13]
		cond = In(name, value)
		self.assertEquals(cond.cql, '{} IN (%s, %s)'.format(name))
		self.assertEquals(cond.values, value)

	def test_set_value(self):
		name, value = 'name', set(['foo', 13])
		cond = In(name, value)
		self.assertEquals(cond.cql, '{} IN (%s, %s)'.format(name))
		self.assertEquals(cond.values, value)

	def test_not_iterable_value(self):
		self.assertRaises(ValidationError, In, 'name', None)
		self.assertRaises(ValidationError, In, 'name', 13)

class TestUsing(TestCase):
	 
	def test_option_single(self):
		cond = Using(ttl=3600)
		self.assertEquals(cond.cql, 'USING TTL %s')
		self.assertEquals(cond.values, [3600])

	def test_option_multi(self):
		kwargs = {'TTL': 3600, 'TIMESTAMP': 3600}
		cond = Using(**kwargs)
		self.assertEquals(cond.cql, 'USING {} %s AND {} %s'.format(*kwargs.keys()))
		self.assertEquals(cond.values, kwargs.values())

	def test_option_timedelta(self):
		kwargs = {'TTL': timedelta(hours=1)}
		cond = Using(**kwargs)
		self.assertEquals(cond.values, [3600])

class TestWhere(TestCase):

	def test_condition_single(self):
		cond = eq('name', 'foo')
		where = Where(cond)
		self.assertEquals(where.cql, cond.cql)
		self.assertEquals(where.values, cond.values)

	def test_condition_multi(self):
		names, values = ['first', 'last'], ['foo', 'bar']
		conditions = [eq(name, value) for name, value in zip(names, values)]
		where = Where(*conditions)
		self.assertEquals(where.cql, ' AND '.join(cond.cql for cond in conditions))
		self.assertEquals(where.values, values)

	def test_invalid_condition_type(self):
		conditions = ['foo']
		self.assertRaises(ValidationError, Where, *conditions)

	def test_none_condition(self):
		conditions = [eq('name', 'foo'), None]
		self.assertRaises(ValidationError, Where, *conditions)

if __name__ == '__main__':
	unittest.main()
