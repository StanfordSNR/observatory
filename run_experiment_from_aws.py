#!/usr/bin/env python

import os
import sys
import argparse
from datetime import datetime
from subprocess import check_call
from slack_post import slack_post, slack_post_img


def main():
    local_sides = {
        'AWS Brazil': '52.67.203.197',
        'AWS California': '52.52.80.245',
        'AWS Korea': '52.79.43.78',
        'AWS India': '35.154.48.15',
    }

    aws_to_ntp_server = {
        'AWS Brazil': 'gps.ntp.br',
        'AWS California': 'time.stanford.edu',
        'AWS Korea': 'ntp.nict.jp',
        'AWS India': 'ntp1.andysen.com',
    }

    remote_sides = {
        'Stanford': 'pi@171.66.3.65',
        'Brazil': 'pi@177.234.144.122',
        'Colombia': 'pi@138.121.201.58',
        'Mexico': 'pi@143.255.56.146',
        'China': 'yanyu@101.6.97.145',
        'Nepal': 'pi@nepal6',  # uses ssh alias, currently only AWS India works
        'India': 'pi@109.73.164.122',
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'local', choices=local_sides.keys(), help='local side')
    parser.add_argument(
        'remote', choices=remote_sides.keys(), help='remote side')
    parser.add_argument(
        '--run-times', metavar='TIMES', action='store', dest='run_times',
        type=int, default=1, help='run times of each test')
    parser.add_argument(
        '--sender-side', choices=['local', 'remote'], action='store',
        dest='sender_side', default='remote',
        help='the side to be data sender (default remote)')
    parser.add_argument(
        '--remote-interface', metavar='INTERFACE', action='store',
        dest='remote_if', help='remote interface to run tunnel on')
    parser.add_argument(
        '--no-setup', action='store_true',
        help='skip running setup of schemes')
    parser.add_argument(
        '--no-ntp', action='store_true',
        help='don\'t check ntp offset of both sides while running')
    parser.add_argument(
        '--skip-analysis', action='store_true',
        help='skip running setup of schemes')
    parser.add_argument(
        '--no-git-pull', action='store_true',
        help='skip updating pantheon repo on local and remote sides')
    parser.add_argument(
        '--bidirectional', action='store_true',
        help='run both --sender-side remote and --sender-side local, '
             'using --sender-side defines which experiment runs first')
    args = parser.parse_args()

    if args.remote_if:
        remote_txt = '%s %s' % (args.remote, args.remote_if)
    else:
        remote_txt = args.remote

    if args.sender_side is 'remote':
        senders_to_run = ['remote']
        if args.bidirectional:
            senders_to_run.append('local')
    else:
        senders_to_run = ['local']
        if args.bidirectional:
            senders_to_run.append('remote')

    test_dir = os.path.expanduser('~/pantheon/test/')
    os.chdir(test_dir)

    experiment_meta_txt = 'Experiment between %s' % args.local
    experiment_meta_txt += ' and %s with ' % args.remote
    experiment_meta_txt += '%d runs ' % args.run_times

    if args.no_git_pull and args.no_setup and not args.bidirectional:
        # Post below should be enough in this case
        pass
    else:
        slack_txt = 'Setting up '
        if args.bidirectional:
            slack_txt += 'bidirectional '
            experiment_meta_txt += 'per side '
        slack_post(slack_txt + 'e' + experiment_meta_txt[1:-1] + '.')

    # Update pantheon git repos on both sides
    if not args.no_git_pull:
        try:
            check_call('git pull --ff-only', shell=True)
            check_call('git submodule update --init --recursive', shell=True)
            # assumption pantheon directory is in ~ on remote side
            remote = remote_sides[args.remote]
            remote_git_prefix = 'ssh %s git -C pantheon ' % remote
            check_call(remote_git_prefix + 'pull --ff-only', shell=True)
            check_call(remote_git_prefix +
                       'submodule update --init --recursive', shell=True)
        except:
            slack_post(experiment_meta_txt + 'failed during git update phase.')
            return

    common_cmd = ('./run.py -r %s:~/pantheon -t 30 --tunnel-server local '
                  '--local-addr %s --local-info "%s" '
                  '--remote-info "%s" --random-order --run-times %s'
                  % (remote_sides[args.remote], local_sides[args.local],
                     args.local, args.remote, args.run_times))
    if args.remote_if:
        common_cmd += ' --remote-interface ' + args.remote_if

    # If using NTP, make sure NTP server we intend to use is up
    if not args.no_ntp:
        ntp_server = aws_to_ntp_server[args.local]
        common_cmd += ' --ntp-addr ' + ntp_server
        try:
            check_call(['ntpdate', '-quv', ntp_server])
        except:
            slack_post(experiment_meta_txt + ' could not sync with ntp server '
                       '%s, aborting.' % ntp_server)
            return

    # Run setup
    if not args.no_setup:
        sys.stderr.write(common_cmd + ' --run-only setup\n')
        try:
            check_call(common_cmd + ' --run-only setup', shell=True)
        except:
            slack_post(experiment_meta_txt + 'failed during setup phase.')
            return

    # Make sure /tmp/pantheon-tmp exists and we can grab experiment lock
    experiment_lock_command = 'mkdir /tmp/pantheon-tmp/experiment_lock'
    try:
        check_call(experiment_lock_command, shell=True)
    except:
        slack_post(experiment_meta_txt + ' could not aquire lock locally to '
                   'run experiment: another experiment could already be '
                   'running or a previous experiment ended messily.')
    try:
        check_call('ssh %s ' % remote_sides[args.remote] +
                   experiment_lock_command, shell=True)
    except:
        slack_post(experiment_meta_txt + ' could not aquire lock remotely to '
                   'run experiment: another experiment could already be '
                   'running or a previous experiment ended messily.')

    for sender_side in senders_to_run:
        do_analysis = not args.skip_analysis
        if sender_side is 'remote':
            uploader = remote_txt
            downloader = args.local
        else:
            uploader = args.local
            downloader = remote_txt

        experiment_title = '%s to %s %d runs' % (uploader, downloader,
                                                 args.run_times)

        try:
            # Clean up test directory
            check_call('rm -rf *.log *.json *.png *.pdf *.out verus_tmp',
                       shell=True)
        except:
            slack_post(experiment_meta_txt + ' could not remove files from'
                       'test directory or pantheon-tmp, proceeding anyway..')

        slack_post('Running experiment uploading from %s.' % experiment_title)

        cmd = common_cmd + ' --sender-side ' + sender_side
        # Run Test
        sys.stderr.write(cmd + ' --run-only test\n')
        try:
            check_call(cmd + ' --run-only test', shell=True)
        except:
            experiment_title += ' FAILED'
            do_analysis = False

        # Pack logs in archive and upload to S3
        date = datetime.utcnow()
        date = date.replace(microsecond=0).isoformat().replace(':', '-')
        date = date[:-3]  # strip seconds

        experiment_file_prefix = '%s-%s' % (date,
                                            experiment_title.replace(' ', '-'))
        src_dir = '%s-logs' % experiment_file_prefix
        try:
            check_call(['mkdir', src_dir])
            check_call('mv *.log *.json ' + src_dir, shell=True)

            src_tar = src_dir + '.tar.xz'
            check_call('tar cJf ' + src_tar + ' ' + src_dir, shell=True)
        except:
            slack_post('Experiment uploading from %s could not create archive '
                       'of results. Probably disk space issue or no results '
                       'existed.' % experiment_title)
            return

        s3_base = 's3://stanford-pantheon/'
        s3_folder = 'real-world-results/%s/' % args.remote
        s3_url = s3_base + s3_folder + src_tar
        try:
            check_call('aws s3 cp ' + src_tar + ' ' + s3_url, shell=True)
        except:
            slack_post('Experiment uploading from %s could not upload to s3.'
                       % experiment_title)
            return

        http_base = 'https://stanford-pantheon.s3.amazonaws.com/'
        http_url = http_base + s3_folder + src_tar
        slack_txt = ('Logs archive of %s uploaded to:\n<%s>\n'
                     'To generate report run:\n`pantheon/analyze/analyze.py '
                     '--s3-link %s`' % (experiment_title, http_url, http_url))
        slack_post(slack_txt)

        sys.stderr.write('Logs archive uploaded to: %s\n' % http_url)

        # Perform analysis and upload results to S3
        if do_analysis:
            cmd = ('../analyze/analyze.py --data-dir ../test/%s' % src_dir)
            try:
                check_call(cmd, shell=True)

                local_pdf = '%s/pantheon_report.pdf' % src_dir
                s3_analysis_folder = s3_folder + 'reports/'
                s3_pdf = experiment_file_prefix + '_report.pdf'
                s3_url = s3_base + s3_analysis_folder + s3_pdf
                check_call(['aws', 's3', 'cp', local_pdf, s3_url])

                http_url = http_base + s3_analysis_folder + s3_pdf
                slack_txt = 'Analysis of %s uploaded to:' % experiment_title
                slack_txt += '\n<%s>\n' % http_url
                slack_post(slack_txt)

                imgs_to_upload = ['pantheon_summary.png']
                # Don't post summary means chart if there is only one run
                if args.run_times > 1:
                    imgs_to_upload.append('pantheon_summary_mean.png')

                for img in imgs_to_upload:
                    local_img = '%s/%s' % (src_dir, img)
                    s3_img = experiment_file_prefix + '_' + img
                    s3_url = s3_base + s3_analysis_folder + s3_img
                    check_call(['aws', 's3', 'cp', local_img, s3_url])
                    img_title = '%s from %s' % (img, experiment_title)
                    http_url = http_base + s3_analysis_folder + s3_img
                    slack_post_img(img_title, http_url)
            except:
                slack_post('Experiment uploading from %s could not perform or '
                           'upload analysis.' % experiment_title)

    try:
        # Clean up files generated
        check_call(['rm', '-rf', src_dir, src_tar])
        # Clean up pantheon unmerged logs on both local and remote
        # also removes experiment lock directory
        pantheon_tmp_rm_cmd = 'rm -rf /tmp/pantheon-tmp'
        check_call(pantheon_tmp_rm_cmd, shell=True)
        check_call('ssh %s %s' % (remote_sides[args.remote],
                                  pantheon_tmp_rm_cmd), shell=True)
    except:
        slack_post('Experiment uploading from %s could not remove files'
                   'from test directory after running experiment.'
                   % experiment_title)
        return


if __name__ == '__main__':
    main()
