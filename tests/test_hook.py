import nose
import angr

import os
location = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../binaries/tests'))

def test_mips():
    MAIN_END = 0x4007D8
    INNER_LOOP = 0x40069C
    OUTER_LOOP = 0x40076C

    p = angr.Project(location + '/mips/test_loops')
    output = []
    def hook1(_):
        output.append(1)

    def hook2(state):
        output.append(2)
        num = state.se.any_int(state.regs.a1)
        string = '%d ' % num
        state.posix.files[1].write(state.BVV(string), state.BVV(len(string), 32))

    p.hook(INNER_LOOP, hook1)
    p.hook(OUTER_LOOP, hook2, length=0x14)

    s = p.surveyors.Explorer(start=p.factory.path(), find=[MAIN_END])
    s.run()

    nose.tools.assert_equal(len(s.found), 1)
    nose.tools.assert_equal(s.found[0].state.posix.dumps(1), ''.join('%d ' % x for x in xrange(100)) + '\n')
    nose.tools.assert_equal(output, [1]*100 + [2]*100)
    # print 'Executed %d blocks' % len(s._f.backtrace)

if __name__ == '__main__':
    test_mips()
